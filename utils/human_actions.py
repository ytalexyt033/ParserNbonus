import random
import asyncio
from playwright.async_api import Page
from config.config import Config

class HumanActions:
    async def random_delay(self):
        delay = random.uniform(*Config.HUMAN_DELAY_RANGE)
        await asyncio.sleep(delay)
    
    async def move_mouse_to_element(self, page: Page, selector: str):
        element = await page.query_selector(selector)
        if element:
            box = await element.bounding_box()
            if box:
                # Move mouse in a human-like curve
                steps = random.randint(3, 7)
                start_x, start_y = random.randint(0, 100), random.randint(0, 100)
                
                for i in range(1, steps + 1):
                    x = start_x + (box['x'] + box['width'] / 2 - start_x) * (i / steps)
                    y = start_y + (box['y'] + box['height'] / 2 - start_y) * (i / steps)
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    async def click_with_delay(self, page: Page, selector: str):
        await self.random_delay()
        await self.move_mouse_to_element(page, selector)
        await self.random_delay()
        await page.click(selector)
        await self.random_delay()
    
    async def type_with_delay(self, page: Page, selector: str, text: str):
        await self.random_delay()
        await self.move_mouse_to_element(page, selector)
        await self.random_delay()
        await page.click(selector)
        await self.random_delay()
        
        for char in text:
            await page.keyboard.type(char, delay=random.uniform(0.05, 0.3))
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.1, 0.5))
    
    async def random_scroll(self, page: Page):
        if random.random() < 0.7:  # 70% chance to scroll
            scroll_amount = random.randint(100, 500)
            scroll_direction = 1 if random.random() < 0.5 else -1
            await page.mouse.wheel(0, scroll_amount * scroll_direction)
            await self.random_delay()