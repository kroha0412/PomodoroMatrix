# analytics/forms.py
"""
Формы для модуля аналитики и статистики.
Только 2 периода: сегодня и 7 дней.
"""

from django import forms
from django.utils import timezone
from datetime import timedelta


class AnalyticsFilterForm(forms.Form):
    """
    Форма для фильтрации данных аналитики по периодам.
    Только сегодня и 7 дней.
    """

    # Опции периодов для выбора
    PERIOD_CHOICES = [
        ('today', '📅 Сегодня'),
        ('7', '📅 Последние 7 дней'),
    ]

    # Поле выбора периода
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='7',  # По умолчанию 7 дней
        required=False,
        label='Период анализа',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'cursor: pointer; min-width: 140px;',
            'onchange': 'this.form.submit()'  # Автоматическая отправка при изменении
        })
    )

    # Метод для получения дат на основе выбранного периода
    def get_date_range(self):
        """
        Возвращает кортеж (start_date, end_date) на основе выбранного периода.
        Если форма не валидна, возвращает период по умолчанию (7 дней).
        """
        if not self.is_valid():
            # По умолчанию - последние 7 дней
            today = timezone.now().date()
            return today - timedelta(days=6), today

        period = self.cleaned_data.get('period', '7')
        today = timezone.now().date()

        # Определяем начальную дату на основе выбранного периода
        if period == 'today':
            start_date = today
        else:  # '7'
            start_date = today - timedelta(days=6)

        return start_date, today

    def clean_period(self):
        """
        Валидация периода - убеждаемся, что значение допустимо.
        """
        period = self.cleaned_data.get('period')
        if period not in ['today', '7']:
            return '7'  # Значение по умолчанию если передано некорректное
        return period