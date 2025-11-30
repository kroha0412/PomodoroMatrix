# users/admin.py
# Импортируем модуль администрирования Django
from django.contrib import admin

# Импортируем стандартный класс для администрирования пользователей
from django.contrib.auth.admin import UserAdmin

# Импортируем стандартную модель пользователя Django
from django.contrib.auth.models import User

# Импортируем нашу кастомную модель настроек пользователя
from .models import UserSettings


# Создаем inline-класс для отображения настроек пользователя на странице пользователя
class UserSettingsInline(admin.StackedInline):
    """
    Inline для отображения настроек Pomodoro прямо на странице пользователя
    StackedInline - поля отображаются вертикально (одно под другим)
    """

    # Указываем модель, которую будем отображать inline
    model = UserSettings

    # Запрещаем удаление inline-записи
    # Поскольку связь один-к-одному, настройки не должны удаляться отдельно от пользователя
    can_delete = False

    # Человекочитаемое название для группы полей (во множественном числе)
    verbose_name_plural = 'Настройки пользователя'

    # Делаем все поля настроек только для чтения
    # Админ может просматривать настройки, но не может их изменять
    readonly_fields = (
    'pomodoro_duration', 'short_break_duration', 'long_break_duration', 'pomodoros_before_long_break')


# Создаем кастомный класс для администрирования пользователей
class CustomUserAdmin(UserAdmin):
    """
    Расширяем стандартный UserAdmin, добавляя наши UserSettings
    с ограничениями прав для безопасности
    """

    # Добавляем наш inline-класс в стандартную админку пользователя
    # Теперь настройки Pomodoro будут отображаться на странице каждого пользователя
    inlines = (UserSettingsInline,)

    # Ограничиваем список отображаемых полей в общем списке пользователей
    # Убираем чувствительные поля и оставляем только информативные
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')

    # Добавляем фильтры для боковой панели
    # Можно фильтровать по статусу персонала, суперпользователям и дате регистрации
    list_filter = ('is_staff', 'is_superuser', 'date_joined')

    # Динамически определяем поля только для чтения в зависимости от контекста
    def get_readonly_fields(self, request, obj=None):
        """
        Возвращает разные наборы readonly полей в зависимости от того,
        редактируем ли мы существующего пользователя или создаем нового
        """
        if obj:
            # editing an existing object - при редактировании существующего пользователя
            # Защищаем важные поля от изменений: логин, email, даты
            return ('username', 'email', 'date_joined', 'last_login')
        # При создании нового пользователя - все поля можно редактировать
        return ()

    # Запрещаем удаление пользователей через админку
    def has_delete_permission(self, request, obj=None):
        """
        Возвращает False чтобы полностью запретить удаление пользователей
        Это защищает от случайного удаления пользовательских данных
        """
        return False


# Отменяем стандартную регистрацию модели User в админке
# Django по умолчанию регистрирует User со стандартным UserAdmin
admin.site.unregister(User)

# Регистрируем модель User с нашим кастомным классом CustomUserAdmin
# Теперь пользователи будут отображаться с нашими настройками и ограничениями
admin.site.register(User, CustomUserAdmin)