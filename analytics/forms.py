# analytics/forms.py
"""
Формы для модуля аналитики и статистики.
Содержит формы фильтрации данных для построения графиков.
"""

from django import forms
from django.utils import timezone
from datetime import timedelta


class AnalyticsFilterForm(forms.Form):
    """
    Форма для фильтрации данных аналитики по периодам.
    Позволяет пользователю выбирать временной диапазон для просмотра статистики.
    """

    # Опции периодов для выбора
    PERIOD_CHOICES = [
        ('7', '📅 Последние 7 дней'),
        ('30', '📅 Последние 30 дней'),
        ('90', '📅 Последние 3 месяца'),
        ('180', '📅 Последние 6 месяцев'),
        ('365', '📅 Последний год'),
    ]

    # Поле выбора периода
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='30',  # По умолчанию 30 дней
        label='Период анализа',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'cursor: pointer;'
        })
    )

    # Опциональные поля для фильтрации по квадрантам
    SHOW_QUADRANT_CHOICES = [
        ('all', 'Все квадранты'),
        ('1', 'Только Квадрант 1 (Важные/Срочные)'),
        ('2', 'Только Квадрант 2 (Важные/Несрочные)'),
        ('3', 'Только Квадрант 3 (Неважные/Срочные)'),
        ('4', 'Только Квадрант 4 (Неважные/Несрочные)'),
    ]

    show_quadrant = forms.ChoiceField(
        choices=SHOW_QUADRANT_CHOICES,
        initial='all',
        label='Фильтр по квадрантам',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'cursor: pointer;'
        })
    )

    # Метод для получения дат на основе выбранного периода
    def get_date_range(self):
        """
        Возвращает кортеж (start_date, end_date) на основе выбранного периода.
        Если форма не валидна, возвращает период по умолчанию (30 дней).
        """
        if not self.is_valid():
            # По умолчанию - последние 30 дней
            today = timezone.now().date()
            return today - timedelta(days=29), today

        period = self.cleaned_data.get('period', '30')
        today = timezone.now().date()

        # Определяем начальную дату на основе выбранного периода
        if period == '7':
            start_date = today - timedelta(days=6)
        elif period == '30':
            start_date = today - timedelta(days=29)
        elif period == '90':
            start_date = today - timedelta(days=89)
        elif period == '180':
            start_date = today - timedelta(days=179)
        elif period == '365':
            start_date = today - timedelta(days=364)
        else:
            start_date = today - timedelta(days=29)  # По умолчанию

        return start_date, today

    def get_quadrant_filter(self):
        """
        Возвращает номер квадранта для фильтрации или None для всех.
        """
        if self.is_valid():
            quadrant = self.cleaned_data.get('show_quadrant', 'all')
            if quadrant != 'all':
                return quadrant
        return None