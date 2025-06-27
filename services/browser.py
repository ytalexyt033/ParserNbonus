import re
import pickle
import os
from pathlib import Path
from datetime import datetime, timedelta
from config.config import Config
from config.constants import LolilandSelectors
from utils.human_actions import HumanActions
import asyncio
from playwright.async_api import async_playwright

class BrowserAutomation:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.human_actions = HumanActions()
    
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await getattr(self.playwright, Config.BROWSER_TYPE).launch(
            headless=Config.HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ru-RU"
        )
        await self.context.add_init_script("""
            delete navigator.__proto__.webdriver;
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        self.page = await self.context.new_page()
    
    async def close(self):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def load_cookies(self, username: str):
        cookie_file = Config.COOKIES_DIR / f"{username}.pkl"
        if cookie_file.exists():
            with open(cookie_file, "rb") as f:
                cookies = pickle.load(f)
                await self.context.add_cookies(cookies)
                return True
        return False
    
    async def save_cookies(self, username: str):
        cookies = await self.context.cookies()
        cookie_file = Config.COOKIES_DIR / f"{username}.pkl"
        with open(cookie_file, "wb") as f:
            pickle.dump(cookies, f)
    
    async def login(self, username: str, password: str):
        await self.page.goto(LolilandSelectors.LOGIN_URL)
        
        if await self.page.query_selector(LolilandSelectors.BONUS_BUTTON):
            return True
        
        await self.human_actions.type_with_delay(
            self.page, 
            LolilandSelectors.USERNAME_INPUT, 
            username
        )
        await self.human_actions.type_with_delay(
            self.page, 
            LolilandSelectors.PASSWORD_INPUT, 
            password
        )
        
        await self.human_actions.click_with_delay(
            self.page, 
            LolilandSelectors.LOGIN_BUTTON
        )
        
        try:
            await self.page.wait_for_selector(LolilandSelectors.BONUS_BUTTON, timeout=10000)
            await self.save_cookies(username)
            return True
        except:
            return False
    
    async def collect_bonus(self, username: str):
        await self.page.goto(LolilandSelectors.BONUS_URL)
        
        bonus_button = await self.page.query_selector(LolilandSelectors.BONUS_BUTTON)
        if not bonus_button:
            return None, None, None
        
        await self.human_actions.click_with_delay(self.page, LolilandSelectors.BONUS_BUTTON)
        
        bonus_content = await self.page.query_selector(LolilandSelectors.BONUS_CONTENT)
        bonus_text = await bonus_content.inner_text()
        bonus_amount = self._parse_bonus_amount(bonus_text)
        
        next_bonus_time = self._parse_next_bonus_time(bonus_text)
        
        balance = await self._parse_balance()
        
        return bonus_amount, next_bonus_time, balance
    
    async def _parse_balance(self):
        try:
            balance_element = await self.page.wait_for_selector(LolilandSelectors.BALANCE_SELECTOR, timeout=5000)
            balance_text = await balance_element.inner_text()
            return int(''.join(filter(str.isdigit, balance_text)))
        except:
            return 0
    
    def _parse_bonus_amount(self, text: str):
        match = re.search(r'(\d+) монет', text)
        return int(match.group(1)) if match else 0
    
    def _parse_next_bonus_time(self, text: str):
        return datetime.now() + timedelta(minutes=5)