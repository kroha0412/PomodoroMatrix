# task_system/urls.py - главный файл маршрутизации проекта

# Импортируем модуль администрирования Django
from django.contrib import admin

# Импортируем функции для работы с URL-маршрутами
# path - для создания отдельных маршрутов
# include - для подключения маршрутов из других приложений
from django.urls import path, include

# Импортируем настройки проекта
from django.conf import settings

# Импортируем функцию для обслуживания медиа-файлов в разработке
from django.conf.urls.static import static

# urlpatterns - основной список маршрутов Django
# Django ищет URL в этом списке сверху вниз
urlpatterns = [
    # URL для админ-панели Django
    # 'admin/' - префикс URL (http://127.0.0.1:8000/admin/)
    # admin.site.urls - автоматически генерирует все URL для админки
    path('admin/', admin.site.urls),

    # Подключаем URL приложения core (главная страница и обучение)
    # '' - означает корневой URL сайта (http://127.0.0.1:8000/)
    # include('core.urls') - включает все маршруты из файла urls.py приложения core
    path('', include('core.urls')),

    path('users/', include('users.urls')),  # Подключаем URL приложения users

    path('tasks/', include('tasks.urls')), # Подключаем URL приложения tasks

    path('pomodoro/', include('pomodoro.urls')),
]

# Это нужно для работы с медиа-файлами (загружаемыми файлами) в режиме разработки
# settings.DEBUG - проверяем, работает ли проект в режиме отладки
if settings.DEBUG:
    # Добавляем маршруты для обслуживания медиа-файлов
    # static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # - создает URL для доступа к загруженным файлам (изображения, документы)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)