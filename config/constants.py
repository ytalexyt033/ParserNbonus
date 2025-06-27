# -*- coding: utf-8 -*-

class LolilandSelectors:
    LOGIN_URL = "https://loliland.ru/ru/login?return_to=/ru/cabinet/bonus"
    BONUS_URL = "https://loliland.ru/ru/cabinet/bonus"
    
    # Селекторы для входа
    USERNAME_INPUT = "input[placeholder='Игровой никнейм']"
    PASSWORD_INPUT = "input[placeholder='Пароль']"
    LOGIN_BUTTON = ".button-p__content-text:has-text('Войти')"
    
    # Селекторы для бонусов
    BONUS_CONTENT = ".cabinet-content__content"
    BONUS_BUTTON = "button[type='button'] span.button-p__content-text:has-text('Получить бонус')"
    
    # Селекторы для парсинга данных
    BALANCE_SELECTOR = "//div[contains(text(), 'Ваш баланс:')]"
    NEXT_BONUS_SELECTOR = "//div[contains(text(), 'Следующий бонус через:')]"