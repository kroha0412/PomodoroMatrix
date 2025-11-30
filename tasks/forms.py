# tasks/forms.py
from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Форма для создания и редактирования задач"""

    class Meta:
        model = Task
        fields = ['title', 'description', 'quadrant', 'priority', 'due_date', 'estimated_pomodoros']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название задачи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание задачи (необязательно)',
                'rows': 3
            }),
            'quadrant': forms.Select(attrs={
                'class': 'form-control'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'estimated_pomodoros': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
        }
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'quadrant': 'Квадрант',
            'priority': 'Приоритет (1-10)',
            'due_date': 'Срок выполнения',
            'estimated_pomodoros': 'Планируемое количество Pomodoro'
        }


class TaskReorderForm(forms.Form):
    """Форма для изменения порядка задач"""
    task_id = forms.IntegerField()
    new_quadrant_id = forms.IntegerField()
    new_order = forms.IntegerField()