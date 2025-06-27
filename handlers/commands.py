from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hcode
from config.config import Config
from database.crud import AccountCRUD, get_db
from services.bonus_collector import BonusCollector
from datetime import datetime, timedelta
import logging
from typing import Optional

router = Router()

# Форматированное сообщение со списком команд
START_MESSAGE = f"""
{hbold('🤖 LoliLand Bonus Bot')}

{hbold('🔐 Админ-команды:')}
/newacc [ник] [пароль] - Добавить аккаунт
/dellacc [ник] - Удалить аккаунт
/collect - Собрать все бонусы
/restart - Перезапустить бота

{hbold('📊 Общие команды:')}
/bonus [ник] - Проверить бонус
/money [ник/all] - Баланс
/help - Это сообщение

{hbold('👑 Администраторы:')} {', '.join(map(str, Config.ADMIN_USER_IDS))}
"""

def check_access(func):
    """Декоратор для проверки прав доступа"""
    async def wrapper(message: types.Message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Разрешаем если: админ ИЛИ разрешенный чат
        if Config.is_trusted_user(user_id) or Config.is_allowed_chat(chat_id):
            return await func(message)
        
        await message.answer("🚫 У вас нет доступа к этой команде!")
    return wrapper

@router.message(Command("start", "help"))
@check_access
async def send_help(message: types.Message):
    """Обработчик команд /start и /help"""
    await message.answer(
        text=START_MESSAGE,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.message(Command("newacc"))
@check_access
async def add_account(message: types.Message):
    """Добавление нового аккаунта (только для админов)"""
    if not Config.is_trusted_user(message.from_user.id):
        await message.answer("🚫 Эта команда только для администраторов!")
        return
    
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.answer("ℹ️ Формат: /newacc [никнейм] [пароль]")
            return
            
        username, password = args[1], args[2]
        db = next(get_db())
        
        if AccountCRUD.get(db, username):
            await message.answer(f"❌ Аккаунт {hcode(username)} уже существует!")
            return
            
        AccountCRUD.create(db, username, password)
        await message.answer(
            text=f"✅ Аккаунт {hcode(username)} успешно создан!",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Ошибка при добавлении аккаунта: {str(e)}")
        await message.answer("❌ Произошла ошибка при создании аккаунта")

@router.message(Command("dellacc"))
@check_access
async def delete_account(message: types.Message):
    """Удаление аккаунта (только для админов)"""
    if not Config.is_trusted_user(message.from_user.id):
        await message.answer("🚫 Эта команда только для администраторов!")
        return
    
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("ℹ️ Формат: /dellacc [никнейм]")
            return
            
        username = args[1]
        db = next(get_db())
        
        if AccountCRUD.delete(db, username):
            await message.answer(
                text=f"✅ Аккаунт {hcode(username)} успешно удален!",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                text=f"❌ Аккаунт {hcode(username)} не найден!",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logging.error(f"Ошибка при удалении аккаунта: {str(e)}")
        await message.answer("❌ Произошла ошибка при удалении аккаунта")

@router.message(Command("collect"))
@check_access
async def collect_bonuses(message: types.Message):
    """Сбор бонусов для всех аккаунтов (только для админов)"""
    if not Config.is_trusted_user(message.from_user.id):
        await message.answer("🚫 Эта команда только для администраторов!")
        return
    
    try:
        msg = await message.answer("🔄 Начинаю сбор бонусов...")
        collector = BonusCollector()
        db = next(get_db())
        accounts = AccountCRUD.get_all(db)
        
        success_count = 0
        for account in accounts:
            try:
                bonus, next_time, balance = await collector.process_account(
                    account.username, 
                    account.password
                )
                if bonus is not None:
                    AccountCRUD.update_balance(db, account.username, balance)
                    success_count += 1
            except Exception as e:
                logging.error(f"Ошибка сбора для {account.username}: {str(e)}")
        
        await msg.edit_text(
            text=f"✅ Сбор завершен! Успешно обработано: {success_count}/{len(accounts)}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Ошибка при сборе бонусов: {str(e)}")
        await message.answer("❌ Произошла ошибка при сборе бонусов")

@router.message(Command("bonus"))
@check_access
async def check_bonus(message: types.Message):
    """Проверка времени до бонуса"""
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("ℹ️ Формат: /bonus [никнейм]")
            return
            
        username = args[1]
        db = next(get_db())
        account = AccountCRUD.get(db, username)
        
        if not account:
            await message.answer(
                text=f"❌ Аккаунт {hcode(username)} не найден!",
                parse_mode="HTML"
            )
            return
            
        # Здесь должна быть логика проверки времени бонуса
        time_left = "3 часа 15 минут"  # Заглушка для примера
        await message.answer(
            text=f"⏳ Бонус для {hcode(username)} будет доступен через: {hbold(time_left)}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Ошибка проверки бонуса: {str(e)}")
        await message.answer("❌ Произошла ошибка при проверке бонуса")

@router.message(Command("money"))
@check_access
async def check_balance(message: types.Message):
    """Проверка баланса"""
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.answer("ℹ️ Формат: /money [никнейм|all]")
            return
            
        target = args[1].lower()
        db = next(get_db())
        
        if target == "all":
            accounts = AccountCRUD.get_all(db)
            total = sum(acc.balance for acc in accounts)
            await message.answer(
                text=f"💰 Общий баланс всех аккаунтов: {hbold(total)} монет",
                parse_mode="HTML"
            )
        else:
            account = AccountCRUD.get(db, target)
            if account:
                await message.answer(
                    text=f"💎 Баланс {hcode(target)}: {hbold(account.balance)} монет",
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    text=f"❌ Аккаунт {hcode(target)} не найден!",
                    parse_mode="HTML"
                )
                
    except Exception as e:
        logging.error(f"Ошибка проверки баланса: {str(e)}")
        await message.answer("❌ Произошла ошибка при проверке баланса")