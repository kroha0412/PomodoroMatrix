# analytics/templatetags/analytics_extras.py
"""
Минимальный набор тегов для аналитики
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Получить значение из словаря по ключу."""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None


@register.filter
def format_time_from_seconds(seconds):
    """Форматировать секунды в минуты или часы."""
    try:
        seconds = int(seconds)
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}ч {minutes}м"
        elif seconds >= 60:
            minutes = seconds // 60
            return f"{minutes} мин"
        else:
            return f"{seconds} сек"
    except (ValueError, TypeError):
        return "0 сек"


@register.filter
def quadrant_name(quadrant_key):
    """Возвращает название квадранта."""
    names = {
        "1": "Важные/Срочные",
        "2": "Важные/Несрочные",
        "3": "Неважные/Срочные",
        "4": "Неважные/Несрочные"
    }
    return names.get(str(quadrant_key), f"Квадрант {quadrant_key}")