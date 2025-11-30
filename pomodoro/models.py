from django.db import models
from django.contrib.auth.models import User  # Импортируем встроенную модель пользователя


# Создаем модель для отслеживания Pomodoro рабочих сессий
class PomodoroSession(models.Model):
    """
    Модель для хранения информации о Pomodoro сессиях пользователей.
    Каждая сессия связана с конкретной задачей и пользователем.
    """

    # Создаем список возможных типов сессий
    SESSION_TYPES = [
        # (значение в базе, человекочитаемое название)
        ('work', 'Работа'),  # Рабочая сессия (25 минут)
        ('short_break', 'Короткий перерыв'),  # Короткий перерыв (5 минут)
        ('long_break', 'Длинный перерыв'),  # Длинный перерыв (15-30 минут)
    ]

    # Создаем список возможных статусов сессии
    STATUS_CHOICES = [
        # (значение в базе, человекочитаемое название)
        ('completed', 'Завершена'),  # Сессия успешно завершена
        ('interrupted', 'Прервана'),  # Сессия была прервана пользователем
        ('cancelled', 'Отменена'),  # Сессия была отменена
    ]

    # Связь "многие-к-одному" с моделью Task из приложения tasks
    # 'tasks.Task' - строковая ссылка на модель в другом приложении
    # on_delete=models.CASCADE - если задача удалена, все ее сессии тоже удаляются
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, verbose_name="Задача")

    # Связь "многие-к-одному" с моделью User
    # on_delete=models.CASCADE - если пользователь удален, все его сессии удаляются
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    # Тип сессии с выбором из предопределенных значений
    # choices=SESSION_TYPES - ограничивает возможные значения списком выше
    # default='work' - значение по умолчанию (рабочая сессия)
    session_type = models.CharField(max_length=15, choices=SESSION_TYPES, default='work', verbose_name="Тип сессии")

    # Время начала сессии
    # auto_now_add=True - автоматически устанавливает текущее время при создании объекта
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Время начала")

    # Время окончания сессии
    # null=True - в базе данных поле может содержать NULL (сессия еще не завершена)
    # blank=True - в формах поле может быть пустым
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Время окончания")

    # Статус сессии с выбором из предопределенных значений
    # choices=STATUS_CHOICES - ограничивает возможные значения списком выше
    # default='completed' - значение по умолчанию
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='completed', verbose_name="Статус")

    # Класс Meta для дополнительных настроек модели
    class Meta:
        # Название модели в единственном числе для отображения в админке
        verbose_name = "Pomodoro сессия"

        # Название модели во множественном числе для отображения в админке
        verbose_name_plural = "Pomodoro сессии"

    # Метод для строкового представления объекта
    def __str__(self):
        # Возвращаем строку с типом сессии и названием задачи
        # get_session_type_display() - метод Django для получения человекочитаемого значения choice поля
        return f"{self.get_session_type_display()} сессия для {self.task.title}"