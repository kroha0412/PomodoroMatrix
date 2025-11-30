# Импортируем модуль администрирования Django
from django.contrib import admin

# Импортируем модель PomodoroSession из текущего приложения
from .models import PomodoroSession


# Создаем класс для настройки отображения модели PomodoroSession в админке
class PomodoroSessionAdmin(admin.ModelAdmin):
    """
    Админка для Pomodoro сессий - только для просмотра аналитики
    Админ может просматривать сессии для анализа продуктивности, но не может их изменять
    """

    # list_display - определяет какие поля показывать в списке всех сессий
    # В списке будут колонки: пользователь, задача, тип сессии, время начала/окончания, статус
    list_display = ('user', 'task', 'session_type', 'start_time', 'end_time', 'status')

    # list_filter - добавляет боковую панель с фильтрами для быстрой фильтрации записей
    # Можно фильтровать сессии по: типу сессии, статусу, дате начала
    list_filter = ('session_type', 'status', 'start_time')

    # search_fields - добавляет поисковую строку в админку
    # Поиск работает по названию связанной задачи и имени пользователя
    # task__title - поиск по полю title модели Task (двойное подчеркивание для связи между моделями)
    # user__username - поиск по полю username модели User
    search_fields = ('task__title', 'user__username')

    # readonly_fields - поля, которые можно только просматривать, но нельзя редактировать
    # ВСЕ поля сессии защищены от изменений - админ может только смотреть
    readonly_fields = ('user', 'task', 'session_type', 'start_time', 'end_time', 'status')

    # Запрещаем добавление новых Pomodoro сессий через админку
    def has_add_permission(self, request):
        """
        Возвращает False чтобы скрыть кнопку "Добавить" в админке
        Сессии должны создаваться только через основное приложение
        """
        return False

    # Запрещаем редактирование существующих Pomodoro сессий
    def has_change_permission(self, request, obj=None):
        """
        Возвращает False чтобы убрать кнопки "Сохранить" и "Редактировать"
        Админ не может изменять исторические данные о сессиях
        """
        return False

    # Запрещаем удаление Pomodoro сессий
    def has_delete_permission(self, request, obj=None):
        """
        Возвращает False чтобы убрать кнопку "Удалить"
        Защищает исторические данные от случайного удаления
        """
        return False

    # Оптимизируем запросы к базе данных
    def get_queryset(self, request):
        """
        Переопределяем метод, который получает QuerySet для отображения в админке
        select_related('user', 'task') предзагружает связанные объекты,
        чтобы избежать проблемы N+1 запроса при отображении списка сессий
        """
        return super().get_queryset(request).select_related('user', 'task')


# Регистрируем модель PomodoroSession в админ-панели с нашим кастомным классом
# Теперь сессии будут отображаться с нашими настройками безопасности
admin.site.register(PomodoroSession, PomodoroSessionAdmin)