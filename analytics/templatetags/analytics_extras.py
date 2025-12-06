# analytics/templatetags/analytics_extras.py
"""
Пользовательские теги шаблонов для модуля аналитики.
Дополнительные фильтры и функции для обработки данных в шаблонах.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Получить значение из словаря по ключу.
    Используется для доступа к данным в шаблонах.
    """
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None


@register.filter
def percentage(value, total):
    """
    Вычислить процент от общего значения.
    """
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_duration(seconds):
    """
    Форматировать продолжительность из секунд в ЧЧ:ММ:СС.
    """
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    except (ValueError, TypeError):
        return "00:00"


@register.filter
def quadrant_color(quadrant_key):
    """
    Возвращает цвет для квадранта по его ключу.
    """
    colors = {
        "1": "#FF6B6B",
        "2": "#4ECDC4",
        "3": "#45B7D1",
        "4": "#96CEB4"
    }
    return colors.get(str(quadrant_key), "#666666")


@register.filter
def quadrant_name(quadrant_key):
    """
    Возвращает название квадранта по его ключу.
    """
    names = {
        "1": "Важные/Срочные",
        "2": "Важные/Несрочные",
        "3": "Неважные/Срочные",
        "4": "Неважные/Несрочные"
    }
    return names.get(str(quadrant_key), "Неизвестный квадрант")


@register.filter
def multiply(value, arg):
    """
    Умножить значение на аргумент.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Разделить значение на аргумент.
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_time_from_seconds(seconds):
    """
    Форматировать секунды в минуты или часы.
    """
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