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

    # Опции периодов для выбора (исправленный список)
    PERIOD_CHOICES = [
        ('today', '📅 Сегодня'),
        ('7', '📅 Последние 7 дней'),
        ('30', '📅 Последние 30 дней'),
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
        if period == 'today':
            start_date = today
        elif period == '7':
            start_date = today - timedelta(days=6)
        else:  # '30' или по умолчанию
            start_date = today - timedelta(days=29)

        return start_date, today