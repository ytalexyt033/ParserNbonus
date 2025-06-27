from config.config import Config
from aiogram.types import Message
from functools import wraps

def chat_access_required(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.chat.id in Config.ALLOWED_CHAT_IDS:
            return await func(message, *args, **kwargs)
        await message.reply("🚫 Доступ запрещен: этот чат не авторизован")
    return wrapper

def private_access_required(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id in Config.ALLOWED_USER_IDS:
            return await func(message, *args, **kwargs)
        await message.reply("🔒 Доступ только для авторизованных пользователей")
    return wrapper

def admin_required(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id in Config.ADMIN_USER_IDS:
            return await func(message, *args, **kwargs)
        await message.reply("⛔ Требуются права администратора")
    return wrapper