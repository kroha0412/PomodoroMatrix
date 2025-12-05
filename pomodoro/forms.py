# pomodoro/forms.py
from django import forms
from users.models import UserSettings


class PomodoroSettingsForm(forms.ModelForm):
    """
    Форма для настройки параметров Pomodoro таймера
    (дублируем из users/forms.py для удобства)
    """

    class Meta:
        model = UserSettings
        fields = ['pomodoro_duration', 'short_break_duration',
                  'long_break_duration', 'pomodoros_before_long_break']

        widgets = {
            'pomodoro_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 60,
                'id': 'pomodoro-duration'
            }),
            'short_break_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 30,
                'id': 'short-break-duration'
            }),
            'long_break_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 60,
                'id': 'long-break-duration'
            }),
            'pomodoros_before_long_break': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
                'id': 'pomodoros-before-long-break'
            }),
        }

        labels = {
            'pomodoro_duration': 'Длительность Pomodoro (мин)',
            'short_break_duration': 'Короткий перерыв (мин)',
            'long_break_duration': 'Длинный перерыв (мин)',
            'pomodoros_before_long_break': 'Pomodoro до длинного перерыва',
        }