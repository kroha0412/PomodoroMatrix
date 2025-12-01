# tasks/forms.py
from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Форма для создания задач (упрощенная - только для 4-го модуля)"""

    class Meta:
        model = Task
        fields = ['title', 'description']  # ТОЛЬКО эти поля для создания
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
        }
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
        }


class TaskReorderForm(forms.Form):
    """Форма для изменения порядка задач"""
    task_id = forms.IntegerField()
    new_quadrant_id = forms.IntegerField()
    new_order = forms.IntegerField()