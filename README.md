# Face_clients
find a client in a database by face

# Проект на FastAPI для распознавания лиц и хранения данных

## Описание
Это веб-приложение на FastAPI, которое распознает людей на фотографиях и сохраняет информацию о них в базе данных. Хранится следующая информация:
- ФИО
- Дата рождения
- Номер телефона
- Email
- Дата оплаты
- Сумма оплаты
При необходимости можно внести данные о клиенте вручную.
Далее, если человек проходит через ресепшен, то автоматически проводится его фотографирвоание и поиск челвоека по фото. если челвоек найден, то выводится информация о нем, в т.ч. сведения об оплате.

## Функционал
1. Управление клиентами:
- Добавление новых клиентов с их личными данными (ФИО, дата рождения, контактная информация).
- Сохранение фотографий клиентов.
- Получение списка всех клиентов.
- Получение списка клиентов, которые не произвели оплату.

Файл database.db (база данных SQLite) создается автоматически при первом запуске приложения, если его нет. 
2. Распознавание лиц:
- Детектирование лиц на изображении с использованием каскадов Хаара.
- Сравнение лиц на двух изображениях с помощью модели FaceNet для определения, есть ли клиент в базе.
- Вывод данных по распознанному по фото клиенту из базы.
3. Визуализация данных:
- Генерация графиков для отображения общей статистики  с использованием Chart.js** (количество клиентов, количество неплательщиков, общая сумма оплат).
- Отображение таблицы с данными по всем клиентам

## Стек технологий
- **Backend:** FastAPI, Python
- **База данных:** SQLite
- **Шаблоны:** HTML с наследованием (Jinja2)
- **Frontend:** Chart.js для дашбордов
- **Дополнительно:** Pandas

## Шаблоны HTML
Проект использует HTML-шаблоны с наследованием от базового шаблона `base.html`. Шаблоны расположены в папке `templates`:
- **base.html** — базовый шаблон с общей структурой страницы (header, main, footer)
- **add_person.html** — форма для добавления нового клиента вручную
- **persons_list.html** — отображение списка клиентов с их данными и статусами оплаты
- **dashboard.html** — дашборд с диаграммами для отображения статистики о клиентах

## Структура проекта 
```markdown
Face_detector/
├── app/
│   ├── main.py                 # Главный файл приложения FastAPI
│   ├── models.py               # Модели базы данных
│   ├── init.py #Файл для инициализации пакета.
│   ├── database.py #Файл для работы с базой данных.
│   ├── face_detector.py #Файл с классом для детектирования лиц с использованием каскадов Хаара.
│   ├── faceNet_try.py #Файл с классом для сравнения лиц с использованием модели FaceNet.
│   ├── Tests/              # Папка с тестами
│   │   ├── test_face_detector.py            # Тесты для проверки работы детектора лиц.
│   │   ├── test_file_extension.py # Тесты для проверки допустимых расширений файлов
│   ├── templates/              # HTML-шаблоны с наследованием
│   │   ├── base.html            # Базовый шаблон
│   │   ├── add_person.html      # Форма добавления клиента
│   │   ├── persons_list.html    # Список клиентов
│   │   └── dashboard.html       # Дашборд со статистикой
│   ├── static/                 # Статические файлы 
│   │   ├── photo                # Папка, где хранятся фото из базы данных 
│   │   ├── haarcascade_frontalface_alt.xml   # Данные для использования каскадов Хаара для распознавания лиц
└── requirements.txt        # Зависимости проекта

## API эндпоинты
- GET/add_person форма (для HTML)
- GET/persons/ Show Persons List - показать всех клиентов (для HTML)
- POST/persons/ Create Person - создать описание клиента
- POST/persons/capture_face_show - создать профильь клиента с фото
- GET/persons_not_paid/ - показать всех клиентов. кто не оплатил
- GET/dashboard - сделать дашборд (всего клиентов, кол-во не оплативших, сумма оплаты всего) (для HTML)
- GET/api/dashboard-data - получить данные для дашборда
- POST/persons/verify_faces - сравнение лица входящего посетителя с фото из базы данных

Полная документация API доступна по адресу:
http://127.0.0.1:8000/docs

## Тестирование
Для тестирования используется pytest. Чтобы запустить тесты, выполните в терминале:
pytest Tests/

## Установка
1. Клонируйте репозиторий:
git clone https://github.com/ваш-пользователь/имя-репозитория.git
cd имя-репозитория

2. Создайте виртуальное окружение:
python -m venv .venv
source .venv/bin/activate    # Для Linux / MacOS
.venv\Scripts\activate       # Для Windows
3. Установите зависимости:
pip install -r requirements.txt

## Запуск через FastApi
uvicorn app.main:app --reload

или если нужно логирование ошибок:
uvicorn app.main:app --reload --log-level debug

Далее в браузере пишем:
http://127.0.0.1:8000/docs

Для работы с пользовательским интерфейсом:
- Для добавления пользователя используйте: http://127.0.0.1:8000/add_person
- Для отображения всех пользователей таблицей используйте: http://127.0.0.1:8000/persons/
- Для постройки графики клиентов, тех, кто не оплатил и суммы оплаты используйте: http://127.0.0.1:8000/dashboard




