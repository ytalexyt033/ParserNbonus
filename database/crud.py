from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Account
from config.config import Config
from datetime import datetime
from typing import Generator

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Генератор сессий БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Инициализация таблиц БД"""
    Base.metadata.create_all(bind=engine)

class AccountCRUD:
    @staticmethod
    def get(db, username: str) -> Account:
        """Получить аккаунт по username"""
        return db.query(Account).filter(Account.username == username).first()

    @staticmethod
    def create(db, username: str, password: str) -> Account:
        """Создать новый аккаунт"""
        account = Account(username=username, password=password)
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db, username: str) -> bool:
        """Удалить аккаунт"""
        account = AccountCRUD.get(db, username)
        if account:
            db.delete(account)
            db.commit()
            return True
        return False

    @staticmethod
    def get_all(db) -> list[Account]:
        """Получить все аккаунты"""
        return db.query(Account).all()

    @staticmethod
    def update_balance(db, username: str, balance: int) -> bool:
        """Обновить баланс аккаунта"""
        account = AccountCRUD.get(db, username)
        if account:
            account.balance = balance
            db.commit()
            return True
        return False