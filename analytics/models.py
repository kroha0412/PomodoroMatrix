from django.db import models
from django.contrib.auth.models import User  # Импортируем встроенную модель пользователя


# Создаем модель для хранения агрегированных данных аналитики
class ProductivityStats(models.Model):
    """
    Модель для хранения ежедневной статистики продуктивности пользователей.
    Содержит агрегированные данные для построения графиков и отчетов.
    """

    # Связь "многие-к-одному" с моделью User
    # on_delete=models.CASCADE - если пользователь удален, его статистика тоже удаляется
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    # Дата статистики (обычно текущая дата)
    # auto_now_add=True - автоматически устанавливает текущую дату при создании объекта
    date = models.DateField(auto_now_add=True, verbose_name="Дата статистики")

    # Общее количество завершенных Pomodoro сессий за день
    # default=0 - по умолчанию 0 завершенных сессий
    total_pomodoros_completed = models.PositiveIntegerField(default=0, verbose_name="Всего завершено Pomodoro")

    # Общее количество завершенных задач за день
    total_tasks_completed = models.PositiveIntegerField(default=0, verbose_name="Всего завершено задач")

    # Время, затраченное на каждый квадрант, в формате JSON
    # JSONField - поле для хранения структур данных в формате JSON
    # default=dict - значение по умолчанию пустой словарь
    # Пример: {"1": 3600, "2": 7200, "3": 1800, "4": 900} (время в секундах)
    time_spent_per_quadrant = models.JSONField(default=dict, verbose_name="Время по квадрантам (JSON)")

    # Специальное поле для времени, затраченного на Квадрант 2 (Важные/Несрочные)
    # Квадрант 2 особенно важен для долгосрочного развития
    # default=0 - по умолчанию 0 секунд
    quadrant_2_time = models.PositiveIntegerField(default=0, verbose_name="Время для Квадранта 2 (сек)")

    # Общее количество запланированных Pomodoro сессий
    planned_pomodoros = models.PositiveIntegerField(default=0, verbose_name="Запланировано Pomodoro")

    # Количество задач, выполненных вовремя (до дедлайна)
    completed_on_time_tasks = models.PositiveIntegerField(default=0, verbose_name="Задачи выполненные в срок")

    # Оценка уровня фокуса пользователя (0-100)
    # FloatField - поле для чисел с плавающей точкой
    # default=0 - по умолчанию 0%
    focus_score = models.FloatField(default=0, verbose_name="Оценка фокуса (0-100)")

    # Общая оценка продуктивности пользователя (0-100)
    productivity_score = models.FloatField(default=0, verbose_name="Оценка продуктивности (0-100)")

    # Количество прерываний во время работы
    interruptions_count = models.PositiveIntegerField(default=0, verbose_name="Количество прерываний")

    # Класс Meta для дополнительных настроек модели
    class Meta:
        # Название модели в единственном числе для отображения в админке
        verbose_name = "Статистика продуктивности"

        # Название модели во множественном числе для отображения в админке
        verbose_name_plural = "Статистика продуктивности"

        # Ограничение уникальности: только одна запись статистики на пользователя в день
        # unique_together - гарантирует, что комбинация полей уникальна
        unique_together = ['user', 'date']

    # Метод для строкового представления объекта
    def __str__(self):
        # Возвращаем строку с именем пользователя и датой статистики
        return f"Статистика {self.user.username} за {self.date}"