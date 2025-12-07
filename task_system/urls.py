# task_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),          # core/
    path('users/', include('users.urls')),   # users/
    path('tasks/', include('tasks.urls')),   # tasks/
    path('pomodoro/', include('pomodoro.urls')),  # pomodoro/
    path('analytics/', include('analytics.urls')), # analytics/
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)