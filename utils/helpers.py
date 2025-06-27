# -*- coding: utf-8 -*-

from datetime import timedelta

def format_timedelta(delta: timedelta) -> str:
    """Форматирует timedelta в читаемый вид на русском языке"""
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    
    # Форматирование часов
    if hours > 0:
        if hours % 10 == 1 and hours % 100 != 11:
            hours_str = f"{hours} час"
        elif 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20):
            hours_str = f"{hours} часа"
        else:
            hours_str = f"{hours} часов"
        parts.append(hours_str)
    
    # Форматирование минут
    if minutes > 0:
        if minutes % 10 == 1 and minutes != 11:
            minutes_str = f"{minutes} минута"
        elif 2 <= minutes % 10 <= 4 and not (12 <= minutes <= 14):
            minutes_str = f"{minutes} минуты"
        else:
            minutes_str = f"{minutes} минут"
        parts.append(minutes_str)
    
    # Форматирование секунд (только если нет часов и минут)
    if seconds > 0 and not (hours or minutes):
        if seconds % 10 == 1 and seconds != 11:
            seconds_str = f"{seconds} секунда"
        elif 2 <= seconds % 10 <= 4 and not (12 <= seconds <= 14):
            seconds_str = f"{seconds} секунды"
        else:
            seconds_str = f"{seconds} секунд"
        parts.append(seconds_str)
    
    return " ".join(parts) if parts else "менее минуты"