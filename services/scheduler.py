import asyncio
from datetime import datetime, timedelta
from database.crud import AccountCRUD
from services.bonus_collector import BonusCollector
from config.config import Config
import logging

class BonusScheduler:
    def __init__(self):
        self.collector = BonusCollector()
        self.is_running = False
        self.task = None

    async def start(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_scheduler())

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def _run_scheduler(self):
        while self.is_running:
            try:
                db = next(AccountCRUD.get_db())
                accounts = AccountCRUD.get_all_accounts(db)
                
                if not accounts:
                    await asyncio.sleep(60)  # Проверяем каждую минуту, если нет аккаунтов
                    continue

                for account in accounts:
                    if not self.is_running:
                        break

                    # Проверяем, можно ли собирать бонус
                    now = datetime.now()
                    if account.next_bonus_time and account.next_bonus_time > now:
                        time_to_wait = (account.next_bonus_time - now).total_seconds()
                        if time_to_wait > 0:
                            logging.info(f"Ждем {time_to_wait} секунд до следующего бонуса для {account.username}")
                            await asyncio.sleep(time_to_wait)

                    # Собираем бонус
                    logging.info(f"Собираем бонус для {account.username}")
                    bonus_amount, next_bonus_time, balance = await self.collector.process_account(
                        account.username, account.password
                    )

                    if bonus_amount is not None:
                        AccountCRUD.update_account_balance(db, account.username, balance)
                        AccountCRUD.update_bonus_time(
                            db, 
                            account.username, 
                            datetime.now(), 
                            next_bonus_time
                        )
                        logging.info(f"Успешно собрано {bonus_amount} монет для {account.username}. Баланс: {balance}")

            except Exception as e:
                logging.error(f"Ошибка в планировщике: {str(e)}")
                await asyncio.sleep(60)  # Ждем перед повторной попыткой