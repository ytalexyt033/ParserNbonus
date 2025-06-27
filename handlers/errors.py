from aiogram import Router
from aiogram.types import ErrorEvent
from config.config import Config
import logging

router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    logging.error("Ошибка в обработчике", exc_info=event.exception)
    
    if event.update.message:
        chat_id = event.update.message.chat.id
        if chat_id in Config.ALLOWED_CHAT_IDS or chat_id in Config.ALLOWED_USER_IDS:
            await event.update.message.answer("⚠️ Произошла ошибка при обработке команды")