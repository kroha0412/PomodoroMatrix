# users/models.py
from django.db import models
from django.contrib.auth.models import User  # Импортируем встроенную модель пользователя
from django.db.models.signals import post_save  # Импортируем сигнал, который срабатывает после сохранения объекта
from django.dispatch import receiver  # Импортируем декоратор для подключения к сигналам


# Создаем модель для хранения персональных настроек пользователя
class UserSettings(models.Model):
    """
    Модель для хранения индивидуальных настроек каждого пользователя.
    Связана с основной моделью User через отношение один-к-одному.
    """

    # Связь "один-к-одному" с моделью User
    # OneToOneField - каждый пользователь имеет только одни настройки и наоборот
    # on_delete=models.CASCADE - если пользователь удален, его настройки тоже удаляются
    # verbose_name - человекочитаемое название для отображения в админке
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    # Длительность рабочей сессии Pomodoro в минутах
    # PositiveIntegerField - поле для положительных целых чисел
    # default=25 - стандартная длительность Pomodoro по методике
    pomodoro_duration = models.PositiveIntegerField(default=25, verbose_name="Длительность Pomodoro (мин)")

    # Длительность короткого перерыва между Pomodoro сессиями
    # default=5 - стандартная длительность короткого перерыва
    short_break_duration = models.PositiveIntegerField(default=5, verbose_name="Длительность короткого перерыва (мин)")

    # Длительность длинного перерыва после нескольких Pomodoro сессий
    # default=15 - стандартная длительность длинного перерыва
    long_break_duration = models.PositiveIntegerField(default=15, verbose_name="Длительность длинного перерыва (мин)")

    # Количество Pomodoro сессий до длинного перерыва
    # default=4 - стандартное значение по методике Pomodoro
    pomodoros_before_long_break = models.PositiveIntegerField(default=4, verbose_name="Pomodoro до длинного перерыва")

    # Класс Meta для дополнительных настроек модели
    class Meta:
        # Название модели в единственном числе для отображения в админке
        verbose_name = "Настройки пользователя"

        # Название модели во множественном числе для отображения в админке
        verbose_name_plural = "Настройки пользователей"

    # Метод для строкового представления объекта
    def __str__(self):
        # Возвращаем строку с именем пользователя для удобного отображения
        return f"Настройки для {self.user.username}"


# Создаем функции-обработчики сигналов для автоматического создания настроек
# @receiver - декоратор, который подключает функцию к сигналу
# post_save - сигнал, который срабатывает после сохранения объекта в базу данных
# sender=User - указываем, что функция реагирует на сохранение объектов модели User
@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    """
    Функция-обработчик сигнала, которая автоматически создает объект UserSettings
    при создании нового пользователя.
    """
    # created=True означает, что был создан новый объект, а не обновлен существующий
    if created:
        # Создаем новый объект UserSettings и связываем его с созданным пользователем
        UserSettings.objects.create(user=instance)


# Второй обработчик сигнала для сохранения настроек
@receiver(post_save, sender=User)
def save_user_settings(sender, instance, **kwargs):
    """
    Функция-обработчик сигнала, которая сохраняет объект UserSettings
    при сохранении пользователя.
    """
    # Сохраняем связанные настройки пользователя
    # usersettings - имя связи в нижнем регистре (Django автоматически создает его)
    instance.usersettings.save()