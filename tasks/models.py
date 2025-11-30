from django.db import models  # Импортируем базовый функционал для моделей
from django.contrib.auth.models import User  # Импортируем встроенную модель пользователя
from django.utils import timezone  # Импортируем утилиты для работы с датами и временем


# Создаем модель для квадрантов матрицы Эйзенхауэра
class EisenhowerQuadrant(models.Model):
    """
    Модель для хранения четырех типов квадрантов матрицы Эйзенхауэра.
    Эта таблица будет предварительно заполнена данными (4 записи).
    """

    # Поле для названия квадранта (например: "Важные и срочные")
    # CharField - поле для короткого текста с ограниченной длиной
    # max_length=100 - максимальная длина текста 100 символов
    # verbose_name - человекочитаемое название для отображения в админке
    name = models.CharField(max_length=100, verbose_name="Название квадранта")

    # Поле для подробного описания назначения квадранта
    # TextField - поле для длинного текста без ограничения длины
    description = models.TextField(verbose_name="Описание")

    # Поле для порядка отображения квадрантов (1, 2, 3, 4)
    # IntegerField - поле для целых чисел
    # Помогает определить последовательность показа квадрантов на странице
    priority_order = models.IntegerField(verbose_name="Порядок отображения (1-4)")

    # Поле для цветового кода в формате HEX (#FF0000 - красный)
    # default='#FFFFFF' - значение по умолчанию (белый цвет), если цвет не указан
    # max_length=7 - потому что HEX-цвет имеет формат #RRGGBB (7 символов)
    color_code = models.CharField(max_length=7, default='#FFFFFF', verbose_name="Цвет (HEX)")

    # Поле для хранения названия иконки или CSS-класса
    # blank=True - поле необязательное для заполнения
    # Позже можно использовать для отображения иконок в интерфейсе
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")

    # Класс Meta для дополнительных настроек модели
    class Meta:
        # Название модели в единственном числе для отображения в админке Django
        verbose_name = "Квадрант Эйзенхауэра"

        # Название модели во множественном числе для отображения в админке Django
        verbose_name_plural = "Квадранты Эйзенхауэра"

        # Поле для сортировки записей по умолчанию
        # Квадранты будут автоматически сортироваться по порядку отображения
        ordering = ['priority_order']

    # Метод __str__ определяет, как будет отображаться объект в админке и в консоли
    def __str__(self):
        # Возвращаем название квадранта вместо стандартного "EisenhowerQuadrant object (1)"
        return self.name


# Создаем модель для задач пользователей
class Task(models.Model):
    """
    Модель для хранения задач пользователей.
    Каждая задача принадлежит пользователю и находится в одном из квадрантов.
    """

    # Создаем список возможных статусов задачи
    # Это помогает избежать опечаток и обеспечивает целостность данных
    STATUS_CHOICES = [
        # (значение в базе, человекочитаемое название)
        ('active', 'Активная'),  # Задача активна и ожидает выполнения
        ('completed', 'Завершена'),  # Задача выполнена
        ('cancelled', 'Отменена'),  # Задача отменена
    ]

    # Связь "многие-к-одному" с моделью User
    # ForeignKey - каждая задача принадлежит одному пользователю
    # on_delete=models.CASCADE - если пользователь удален, удаляются все его задачи
    # verbose_name - отображаемое название связи
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    # Связь "многие-к-одному" с моделью EisenhowerQuadrant
    # on_delete=models.PROTECT - защита от удаления квадранта, если есть задачи в нем
    quadrant = models.ForeignKey(EisenhowerQuadrant, on_delete=models.PROTECT, verbose_name="Квадрант")

    # Заголовок задачи - краткое описание
    # max_length=200 - максимальная длина 200 символов
    title = models.CharField(max_length=200, verbose_name="Заголовок")

    # Подробное описание задачи
    # blank=True - поле может быть пустым (необязательное для заполнения)
    description = models.TextField(blank=True, verbose_name="Описание")

    # Статус задачи с выбором из предопределенных значений
    # choices=STATUS_CHOICES - ограничивает возможные значения списком выше
    # default='active' - значение по умолчанию при создании новой задачи
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")

    # Приоритет задачи внутри квадранта (1-10, где 1 - наивысший приоритет)
    # PositiveIntegerField - поле для положительных целых чисел
    # default=1 - значение по умолчанию
    priority = models.PositiveIntegerField(default=1, verbose_name="Приоритет (1-10)")

    # Срок выполнения задачи (дата и время)
    # null=True - в базе данных поле может содержать NULL
    # blank=True - в формах поле может быть пустым
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")

    # Планируемое количество Pomodoro сессий для выполнения задачи
    # default=1 - по умолчанию предполагается 1 Pomodoro
    estimated_pomodoros = models.PositiveIntegerField(default=1, verbose_name="Планируемое количество Pomodoro")

    # Фактически выполнено Pomodoro сессий для этой задачи
    # default=0 - при создании задачи выполнено 0 сессий
    completed_pomodoros = models.PositiveIntegerField(default=0, verbose_name="Выполнено Pomodoro")

    # Дата и время создания задачи
    # auto_now_add=True - автоматически устанавливает текущее время при создании объекта
    # Нельзя изменить вручную
    created_at = models.DateTimeField(auto_now_add=True)

    # Дата и время последнего обновления задачи
    # auto_now=True - автоматически обновляет время при каждом сохранении объекта
    updated_at = models.DateTimeField(auto_now=True)

    # Дата и время фактического выполнения задачи
    # Заполняется когда статус меняется на 'completed'
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Фактическое время выполнения")

    # Класс Meta для дополнительных настроек модели Task
    class Meta:
        # Название модели в единственном числе
        verbose_name = "Задача"

        # Название модели во множественном числе
        verbose_name_plural = "Задачи"

        # Порядок сортировки задач по умолчанию:
        # 1. По порядку квадранта (priority_order из модели EisenhowerQuadrant)
        # 2. По приоритету задачи (от высшего к низшему)
        # 3. По дате создания (от старых к новым)
        ordering = ['quadrant__priority_order', 'priority', 'created_at']

    # Метод для строкового представления объекта
    def __str__(self):
        # Возвращаем заголовок задачи для удобного отображения
        return self.title

class Task(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    quadrant = models.ForeignKey(EisenhowerQuadrant, on_delete=models.PROTECT, verbose_name="Квадрант")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    priority = models.PositiveIntegerField(default=1, verbose_name="Приоритет (1-10)")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")
    estimated_pomodoros = models.PositiveIntegerField(default=1, verbose_name="Планируемое количество Pomodoro")
    completed_pomodoros = models.PositiveIntegerField(default=0, verbose_name="Выполнено Pomodoro")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Фактическое время выполнения")
    display_order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")  # ← ДОБАВИЛИ

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['quadrant__priority_order', 'display_order', 'priority', 'created_at']

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