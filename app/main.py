import os
import cv2
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from app.database import SessionLocal, init_db
from app.models import Person, PersonFactory
from pydantic import BaseModel
from datetime import date
from pathlib import Path
import io
import matplotlib.pyplot as plt
from fastapi.responses import StreamingResponse
from app.face_detector import FaceDetectorHaar
from app.faceNet_try import FaceNetVerify
from fastapi.middleware.cors import CORSMiddleware

# Путь к папке с фото
PHOTO_DIR = "static/photo"

# Экземпляр детектора
detector = FaceDetectorHaar()

# Экземпляр для сравнения фото
face_recognizer = FaceNetVerify()

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Получаем абсолютный путь к папке с файлами
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")  # Путь до папки с шаблонами
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Инициализация Jinja2Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Папка для сохранения фото
PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "photo")

# Проверим, существует ли папка для фотографий, если нет - создадим
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Pydantic-модель для создания пользователя
class PersonCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    phone_number: str
    email: str
    payment_date: date
    payment_amount: float

    # добавляем настройку, чтобы использовать from_orm
    class Config:
        from_attributes = True

# Фиксируем подключение к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоиинт для отображения HTML-шаблона создания клиента
@app.get("/add_person", response_class=HTMLResponse)
def show_add_person_form(request: Request):
    return templates.TemplateResponse("add_person.html", {"request": request})

# Эндпоинт для создания нового пользователя вручную без фото с исползованием Factory
"""
Валидация с использованием Pydantic и FastAPI. Ббудем проверять:
ФИО – не пустое, минимум 3 символа.
Дата рождения – валидная дата в формате YYYY-MM-DD, не больше текущей даты.
Номер телефона – соответствует формату российского номера.
Email – валидный email.
Дата оплаты – валидная дата в формате YYYY-MM-DD, не больше текущей даты.
Сумма оплаты – положительное число.

@app.post("/persons/")
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    # Используем фабрику для создания объекта Person
    db_person = PersonFactory.create_person(person)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person
"""

@app.post("/persons/")
def create_person(
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(...),
    birth_date: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    payment_date: str = Form(...),
    payment_amount: float = Form(...),
    db: Session = Depends(get_db)
):
    # Проверка дат
    try:
        birth_date = date.fromisoformat(birth_date)
        payment_date = date.fromisoformat(payment_date)
        if birth_date > date.today():
            raise ValueError("Дата рождения не может быть в будущем.")
        if payment_date > date.today():
            raise ValueError("Дата оплаты не может быть в будущем.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Создаем объект Person с валидацией через Pydantic
    try:
        person_data = PersonCreate(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            birth_date=birth_date,
            phone_number=phone_number,
            email=email,
            payment_date=payment_date,
            payment_amount=payment_amount
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Используем фабрику для создания объекта
    db_person = PersonFactory.create_person(person_data)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

"""
# Эндпоинт для получения данных пользователей с фото
@app.get("/persons/")
def get_all_persons(db: Session = Depends(get_db)):
    persons = db.query(Person).all()

    result = []
    for person in persons:
        person_data = {key: value for key, value in person.__dict__.items() if not key.startswith('_')}
        if person.photo_path:
            person_data["photo_url"] = f"/static/photo/{os.path.basename(person.photo_path)}"
        result.append(person_data)
    return result
"""

@app.get("/persons/")  # URL для отображения списка пользователей
def show_persons_list(request: Request, db: Session = Depends(get_db)):
    # Получаем всех пользователей из базы данных
    persons = db.query(Person).all()

    # Передаем данные в шаблон для рендеринга
    return templates.TemplateResponse("persons_list.html", {"request": request, "persons": persons})

@app.post("/persons/capture_face_show/")
async def capture_face_and_save(
        person: PersonCreate,  # Данные о человеке из тела запроса
        db: Session = Depends(get_db)
):
    # Открываем камеру (0 — это индекс камеры по умолчанию)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Не удалось открыть камеру")

    db_person = None  # Переменная для хранения записи о человеке

    # Делаем несколько попыток захвата изображения
    for i in range(100):  # повторяем процесс 100 раз, т.к. сразу может не найтись лицо
        ret, frame = cap.read()  # Читаем кадр с камеры

        if not ret:
            raise HTTPException(status_code=500, detail="Не удалось захватить изображение с камеры")

        # Детектируем лицо на кадре
        faces, _ = detector.detect_faces(frame)

        if len(faces) > 0:
            # Сохраняем изображение в папку static/photo
            photo_filename = f"{person.first_name}_{person.last_name}_{i}.jpg"
            photo_path = os.path.join(PHOTO_DIR, photo_filename)
            cv2.imwrite(photo_path, frame)  # Сохраняем изображение

            # Сохраняем путь к фото в базе данных
            db_person = Person(
                first_name=person.first_name,
                last_name=person.last_name,
                middle_name=person.middle_name,
                birth_date=person.birth_date,
                phone_number=person.phone_number,
                email=person.email,
                payment_date=person.payment_date,
                payment_amount=person.payment_amount,
                photo_path=f"/static/photo/{photo_filename}"  # Путь к фото, доступный через URL
            )

            break  # Если лицо найдено, выходим из цикла

    cap.release()  # Закрываем камеру после завершения работы с ней

    # Если лицо не найдено
    if db_person is None:
        raise HTTPException(status_code=400, detail="Лицо не распознано на изображении")

    db.add(db_person)  # Добавляем запись в базу данных
    db.commit()
    db.refresh(db_person)

    return {"message": "Фото и данные успешно сохранены"}


# Эндпоинт для получения данных неплательщиков
@app.get("/persons_not_paid/")
def get_all_persons_not_paid(db: Session = Depends(get_db)):
    not_paid = db.query(Person).filter(Person.payment_amount == 0).all()
    return [PersonCreate.from_orm(person) for person in not_paid]
# Эндпоинт для получения данных о количестве клиентов, неплательщиков и уплаченной сумме
'''
@app.get("/dashboard/")
def get_dashboard_data(db: Session = Depends(get_db)):
    total_clients = db.query(Person).count()
    not_paid = db.query(Person).filter(Person.payment_amount == 0).count()
    total_paid = db.query(Person.payment_amount).filter(Person.payment_amount != None).all()

    total_paid_sum = (sum([x[0] for x in total_paid if x[0] is not None]))/1000

    # Создаем график
    fig, ax = plt.subplots()
    ax.bar(['Total Clients', 'Not Paid', 'Total Paid,thousands'], [total_clients, not_paid, total_paid_sum])
    ax.set_ylabel('Values')

    # Сохраняем график в памяти (в байтах)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
'''

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/dashboard-data")
def get_dashboard_data(db: Session = Depends(get_db)):
    total_clients = db.query(Person).count()
    not_paid = db.query(Person).filter(Person.payment_amount == 0).count()
    total_paid = db.query(Person.payment_amount).filter(Person.payment_amount != None).all()

    total_paid_sum = sum([x[0] for x in total_paid if x[0] is not None]) / 1000

    # Возвращаем данные в формате JSON
    return JSONResponse({
        "total_clients": total_clients,
        "not_paid": not_paid,
        "total_paid_sum_thousands": total_paid_sum
    })




@app.post("/persons/verify_faces/")
async def verify_faces(
        db: Session = Depends(get_db)
):
    # Открываем камеру (0 — это индекс камеры по умолчанию)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Не удалось открыть камеру")

    is_matched = False  # Флаг для отслеживания совпадения
    matched_person = None  # Хранение данных о найденном человеке
    is_match = False  # Инициализация переменной is_match

    # Делаем несколько попыток захвата изображения
    for i in range(100):  # повторяем процесс 100 раз, т.к. сразу может не найтись лицо
        ret, frame = cap.read()  # Читаем кадр с камеры

        if not ret:
            raise HTTPException(status_code=500, detail="Не удалось захватить изображение с камеры")

        # Сохраняем изображение в папку временно для сравнения
        captured_photo_path = os.path.join(PHOTO_DIR, "temp_captured.jpg")
        cv2.imwrite(captured_photo_path, frame)
        #print(captured_photo_path)
        # Получаем всех людей из базы данных
        all_persons = db.query(Person).all()

        # Сравниваем с каждым фото в базе данных
        for db_person in all_persons:
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Папка, где находится текущий файл

            # Проверяем наличие пути к фото в БД
            if db_person.photo_path:
                db_photo_path = db_person.photo_path.replace('/static', 'static')  # Преобразуем в относительный путь
                db_photo_path = db_photo_path.replace('\\', '/')  # Заменяем слэши на unix-стиль
                print(db_photo_path)

                # Проверяем, существует ли файл
                db_photo_path = os.path.join(base_dir, db_photo_path)
                db_photo_path = Path(base_dir) / db_photo_path

                if os.path.exists(db_photo_path):
                    is_match = face_recognizer.verify_faces(captured_photo_path, db_photo_path)
                    print(is_match)

                    if is_match:
                        is_matched = True
                        matched_person = db_person
                        break  # Останавливаем цикл, если совпадение найдено

        if is_matched:
            break  # Если лицо найдено, выходим из внешнего цикла

    cap.release()  # Закрываем камеру после завершения работы с ней
    os.remove(captured_photo_path)  # Удаляем временное фото

    # Проверяем флаг is_matched
    if is_matched and matched_person:
        return {
            "id": matched_person.id_client,
            "first_name": matched_person.first_name,
            "last_name": matched_person.last_name,
            "middle_name": matched_person.middle_name,
            "birth_date": matched_person.birth_date,
            "phone_number": matched_person.phone_number,
            "email": matched_person.email,
            "payment_date": matched_person.payment_date,
            "payment_amount": matched_person.payment_amount
        }
    else:
        return {"message": "Человек отсутствует в базе"}
# Инициализируем базу данных при запуске
init_db()


