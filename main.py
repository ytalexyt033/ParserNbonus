from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config.config import Config
from handlers import commands, errors
from services.scheduler import BonusScheduler
import asyncio
import logging
from database.crud import init_db
import threading

async def startup_notify(bot: Bot):
    """Отправка уведомлений при запуске бота"""
    # Отправка админам в ЛС
    for admin_id in Config.ADMIN_USER_IDS:
        try:
            await bot.send_message(
                admin_id,
                "✅ Бот успешно запущен!\n"
                "Используйте /help для списка команд",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")

    # Отправка в основной чат
    if Config.MAIN_CHAT_ID:
        try:
            await bot.send_message(
                Config.MAIN_CHAT_ID,
                "🤖 Бот запущен и готов к работе!\n"
                "Напишите /help для списка команд",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error(f"Ошибка отправки в чат {Config.MAIN_CHAT_ID}: {e}")

async def start_bot():
    """Основная функция запуска бота"""
    try:
        # Инициализация
        Config.create_dirs()
        init_db()
        
        # Настройка логгирования
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logger = logging.getLogger(__name__)

        # Создание бота
        bot = Bot(
            token=Config.TELEGRAM_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        # Отправка уведомлений о запуске
        await startup_notify(bot)

        # Настройка диспетчера
        dp = Dispatcher()
        dp.include_router(commands.router)
        dp.include_router(errors.router)

        # Запуск планировщика
        scheduler = BonusScheduler()
        asyncio.create_task(scheduler.start())

        logger.info("Бот успешно запущен")
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
        raise

def run_console_manager():
    """Запуск консольного менеджера"""
    from utils.console_manager import console_manager
    asyncio.run(console_manager())

if __name__ == "__main__":
    # Запуск в отдельных потоках
    bot_thread = threading.Thread(
        target=asyncio.run,
        args=(start_bot(),),
        name="Bot Thread"
    )
    
    console_thread = threading.Thread(
        target=run_console_manager,
        name="Console Manager Thread"
    )

    bot_thread.start()
    console_thread.start()

    bot_thread.join()
    console_thread.join()