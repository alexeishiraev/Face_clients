"""
Отвечает за структуру таблиц в базе данных
Все классы наследуются от Base

"""
from sqlalchemy import Column, Integer, String, Float, Date, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr
from datetime import date

Base = declarative_base()

class Person(Base):
    """
    Модель для хранения данных о клиенте
    формируем базу данных о клиенте, проверяем вводимые вручную данные
    - ФИО
    - дата рождения
    - контакты (номер телефона, e-mail) - уникальные
    - дата и сумма оплаты
    """

    __tablename__ = "persons"
    id_client = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    birth_date = Column(Date, nullable=False)
    phone_number = Column(String, unique=True, nullable=False) # ожидаем, что будет уникальный номер
    email = Column(String, unique=True, nullable=False)# ожидаем, что будет уникальный адрес почты
    payment_date = Column(Date, nullable=True)
    payment_amount = Column(Float, nullable=True)
    photo_path = Column(String)  # Путь к фото


class PersonCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    birth_date: date
    phone_number: str
    email: EmailStr
    payment_date: date
    payment_amount: float

    class Config:
        orm_mode = True

"""
class PersonFactory:
    @staticmethod
    def create_person(person_data, photo_path=None):
      
        Создает экземпляр Person из данных.

        :param person_data: объект с аттрибутами first_name, last_name, middle_name, birth_date, phone_number, email, payment_date, payment_amount.
        :param photo_path: путь к фото клиента (необязательный параметр).
        :return: Экземпляр класса Person
       
        if not person_data.first_name or not person_data.last_name or not person_data.birth_date:
            raise ValueError("First name, last name and birth date are required.")

        # Создаем и возвращаем объект Person
        db_person = Person(
            first_name=person_data.first_name,
            last_name=person_data.last_name,
            middle_name=person_data.middle_name,
            birth_date=person_data.birth_date,
            phone_number=person_data.phone_number,
            email=person_data.email,
            payment_date=person_data.payment_date,
            payment_amount=person_data.payment_amount,
            photo_path=photo_path
        )
        return db_person
"""

class PersonFactory:
    """
    Фабрика для создания экземпляров Person
    """
    @staticmethod
    def create_person(person_data: PersonCreate, photo_path=None):

        db_person = Person(
            first_name=person_data.first_name,
            last_name=person_data.last_name,
            middle_name=person_data.middle_name,
            birth_date=person_data.birth_date,
            phone_number=person_data.phone_number,
            email=person_data.email,
            payment_date=person_data.payment_date,
            payment_amount=person_data.payment_amount,
            photo_path=photo_path
        )
        return db_person