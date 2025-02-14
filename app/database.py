"""
Обеспечиваем соединение с базой данных
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

DATABASE_URL = "sqlite:///./database.db"  # Подключение к SQLite

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создаем таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)
