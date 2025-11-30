# Импортируем модуль администрирования Django
from django.contrib import admin

# Импортируем стандартную модель пользователя (может понадобиться для связей)
from django.contrib.auth.models import User

# Импортируем наши модели из текущего приложения
from .models import EisenhowerQuadrant, Task


# Класс для настройки отображения модели EisenhowerQuadrant в админке
class EisenhowerQuadrantAdmin(admin.ModelAdmin):
    """
    Админка для квадрантов - доступна только для просмотра и минимального редактирования
    Квадранты - системные данные, не привязанные к пользователям
    """

    # list_display - определяет какие поля показывать в списке записей
    list_display = ('name', 'priority_order', 'color_code', 'icon')

    # list_editable - поля, которые можно редактировать прямо из списка без захода в запись
    list_editable = ('priority_order', 'color_code')

    # search_fields - добавляет поисковую строку, поиск работает по этим полям
    search_fields = ('name', 'description')

    # list_filter - добавляет боковую панель с фильтрами по указанным полям
    list_filter = ('priority_order',)

    # Запрещаем удаление квадрантов через админку
    # Этот метод переопределяет стандартное поведение - возвращает False чтобы запретить удаление
    def has_delete_permission(self, request, obj=None):
        return False  # Никто не может удалять квадранты

    # Запрещаем добавление новых квадрантов (у нас только 4 фиксированных)
    # Возвращает False чтобы скрыть кнопку "Добавить" в админке
    def has_add_permission(self, request):
        return False  # Никто не может добавлять новые квадранты


# Класс для настройки отображения модели Task в админке
class TaskAdmin(admin.ModelAdmin):
    """
    Админка для задач с ограниченными правами.
    Админ может только просматривать системную аналитику, но не редактировать чужие задачи.
    """

    # Поля для отображения в списке задач
    list_display = ('title', 'user', 'quadrant', 'status', 'priority', 'created_at')

    # Фильтры для боковой панели - можно фильтровать по квадранту, статусу и дате создания
    list_filter = ('quadrant', 'status', 'created_at')

    # Поля для поиска - можно искать по заголовку и описанию задачи
    search_fields = ('title', 'description')

    # readonly_fields - поля, которые можно только просматривать, но нельзя редактировать
    # Все основные поля задачи защищены от изменений
    readonly_fields = ('user', 'title', 'description', 'quadrant', 'created_at', 'updated_at')

    # Убираем возможность массового редактирования - пустой кортеж означает, что нельзя редактировать прямо из списка
    list_editable = ()

    # Ограничиваем queryset - показываем только задачи для системного анализа
    def get_queryset(self, request):
        # Получаем стандартный QuerySet от родительского класса
        qs = super().get_queryset(request)
        # Админ видит все задачи, но только для аналитики
        # select_related оптимизирует запросы, загружая связанные объекты user и quadrant одним запросом
        return qs.select_related('user', 'quadrant')

    # Запрещаем редактирование задач - возвращает False чтобы убрать кнопки "Сохранить" и "Редактировать"
    def has_change_permission(self, request, obj=None):
        return False  # Админ не может изменять задачи

    # Запрещаем удаление задач - возвращает False чтобы убрать кнопку "Удалить"
    def has_delete_permission(self, request, obj=None):
        return False  # Админ не может удалять задачи

    # Запрещаем создание задач от имени других пользователей - возвращает False чтобы скрыть кнопку "Добавить"
    def has_add_permission(self, request):
        return False  # Админ не может создавать задачи

    # Группируем поля только для просмотра - fieldsets организует поля на форме редактирования
    fieldsets = (
        # Первая группа полей - основная информация о задаче
        ('Информация о задаче (только просмотр)', {
            'fields': ('user', 'title', 'description', 'quadrant')  # Все поля только для чтения
        }),
        # Вторая группа - статус и метрики задачи
        ('Статус и метрики (только просмотр)', {
            'fields': ('status', 'priority', 'due_date')  # Информация о статусе и приоритете
        }),
        # Третья группа - Pomodoro метрики
        ('Pomodoro метрики (только просмотр)', {
            'fields': ('estimated_pomodoros', 'completed_pomodoros', 'completed_at')  # Данные о Pomodoro сессиях
        }),
        # Четвертая группа - системная информация (свернута по умолчанию)
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),  # Автоматические временные метки
            'classes': ('collapse',)  # Сворачиваем по умолчанию чтобы не занимать место
        }),
    )


# Регистрируем модель EisenhowerQuadrant с настройками EisenhowerQuadrantAdmin
admin.site.register(EisenhowerQuadrant, EisenhowerQuadrantAdmin)

# Регистрируем модель Task с настройками TaskAdmin
admin.site.register(Task, TaskAdmin)