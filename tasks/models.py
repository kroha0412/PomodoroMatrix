# tasks/models.py
from django.db import models  # Импортируем models ДО использования!
from django.contrib.auth.models import User
from django.utils import timezone


# Сначала должны быть импорты, затем объявления моделей

class EisenhowerQuadrant(models.Model):
    """
    Модель для хранения четырех типов квадрантов матрицы Эйзенхауэра.
    Эта таблица будет предварительно заполнена данными (4 записи).
    """
    name = models.CharField(max_length=100, verbose_name="Название квадранта")
    description = models.TextField(verbose_name="Описание")
    priority_order = models.IntegerField(verbose_name="Порядок отображения (1-4)")
    color_code = models.CharField(max_length=7, default='#FFFFFF', verbose_name="Цвет (HEX)")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")

    class Meta:
        verbose_name = "Квадрант Эйзенхауэра"
        verbose_name_plural = "Квадранты Эйзенхауэра"
        ordering = ['priority_order']

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Модель для хранения задач пользователей.
    Каждая задача принадлежит пользователю и находится в одном из квадрантов.
    """
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    # ИЗМЕНЕНИЕ: Делаем квадрант необязательным при создании задачи
    quadrant = models.ForeignKey(EisenhowerQuadrant, on_delete=models.PROTECT,
                                 verbose_name="Квадрант", null=True, blank=True)

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")

    # Порядок отображения ВНУТРИ квадранта
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    # Поля для 5-го модуля (выполнение) - можно оставить
    priority = models.PositiveIntegerField(default=1, verbose_name="Приоритет (1-10)")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")
    estimated_pomodoros = models.PositiveIntegerField(default=1, verbose_name="Планируемое количество Pomodoro")
    completed_pomodoros = models.PositiveIntegerField(default=0, verbose_name="Выполнено Pomodoro")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Фактическое время выполнения")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['quadrant__priority_order', 'display_order', 'created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем порядок отображения при создании
        if not self.pk:
            max_order = Task.objects.filter(
                user=self.user,
                quadrant=self.quadrant
            ).aggregate(models.Max('display_order'))['display_order__max'] or 0
            self.display_order = max_order + 1
        super().save(*args, **kwargs)