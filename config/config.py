import os
from pathlib import Path
from typing import Set

class Config:
    # Основные настройки
    TELEGRAM_TOKEN = "7772870425:AAF-9pH-ly4l1j5C-wW3K-tBjPJtlypg0hU"
    DATABASE_URL = "sqlite:///accounts.db"
    BROWSER_TYPE = "chromium"
    HEADLESS = False
    
    # Пути к директориям
    BASE_DIR = Path(__file__).parent.parent
    SCREENSHOTS_DIR = BASE_DIR / "assets" / "screenshots"
    COOKIES_DIR = BASE_DIR / "assets" / "cookies"
    DB_DIR = BASE_DIR / "database"
    
    # Настройки времени
    MAX_ACCOUNT_TIME = 120
    HUMAN_DELAY_RANGE = (1, 5)
    
    # Настройки доступа
    MAIN_CHAT_ID = -1002832408684
    ADMIN_USER_IDS: Set[int] = {537496157}  # Ваш ID
    ALLOWED_CHAT_IDS: Set[int] = {MAIN_CHAT_ID}
    ALLOWED_USER_IDS: Set[int] = ADMIN_USER_IDS

    @classmethod
    def create_dirs(cls):
        """Создает все необходимые директории"""
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(cls.COOKIES_DIR, exist_ok=True)
        os.makedirs(cls.DB_DIR, exist_ok=True)
        
        if not (cls.DB_DIR / "accounts.db").exists():
            (cls.DB_DIR / "accounts.db").touch()

    @classmethod
    def is_trusted_user(cls, user_id: int) -> bool:
        """Проверяет, является ли пользователь админом"""
        return user_id in cls.ADMIN_USER_IDS

    @classmethod
    def is_allowed_chat(cls, chat_id: int) -> bool:
        """Проверяет, разрешен ли чат"""
        return chat_id in cls.ALLOWED_CHAT_IDS