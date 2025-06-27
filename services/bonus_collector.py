from datetime import datetime, timedelta
import asyncio
from typing import Tuple, Optional
from .browser import BrowserAutomation
from database.crud import AccountCRUD
from config.config import Config
from utils.human_actions import HumanActions

class BonusCollector:
    def __init__(self):
        self.browser = BrowserAutomation()
        self.human_actions = HumanActions()
    
    async def process_account(self, username: str, password: str) -> Tuple[Optional[int], Optional[datetime], Optional[int]]:
        """Process an account and return (bonus_amount, next_bonus_time, balance)"""
        start_time = datetime.now()
        
        try:
            await self.browser.start()
            
            # Try to load cookies first
            cookies_loaded = await self.browser.load_cookies(username)
            if not cookies_loaded or not await self.browser.login(username, password):
                # If cookies not loaded or login failed, try fresh login
                if not await self.browser.login(username, password):
                    return None, None, None
            
            # Process bonus collection
            bonus_amount, next_bonus_time, balance = await self.browser.collect_bonus(username)
            
            # Calculate remaining time to stay on the page (to reach 2 minutes)
            processing_time = (datetime.now() - start_time).total_seconds()
            remaining_time = max(0, Config.MAX_ACCOUNT_TIME - processing_time)
            
            if remaining_time > 0:
                # Simulate human-like activity during remaining time
                await self._simulate_activity(remaining_time)
            
            return bonus_amount, next_bonus_time, balance
        
        except Exception as e:
            print(f"Error processing account {username}: {str(e)}")
            return None, None, None
        
        finally:
            await self.browser.close()
    
    async def _simulate_activity(self, duration: float):
        """Simulate human-like activity for the remaining time"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < duration:
            # Randomly choose an activity
            activity = random.choice([
                self._random_scroll,
                self._random_clicks,
                self._random_navigation
            ])
            
            await activity()
            await self.human_actions.random_delay()
    
    async def _random_scroll(self):
        await self.browser.page.mouse.wheel(0, random.randint(100, 500))
    
    async def _random_clicks(self):
        elements = await self.browser.page.query_selector_all("a, button")
        if elements:
            await self.human_actions.click_with_delay(
                self.browser.page,
                elements[random.randint(0, len(elements) - 1)]
            )
    
    async def _random_navigation(self):
        links = await self.browser.page.query_selector_all("a")
        if links:
            await links[random.randint(0, len(links) - 1)].click()
            await asyncio.sleep(random.uniform(1, 3))
            await self.browser.page.go_back()