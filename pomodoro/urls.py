# pomodoro/urls.py
from django.urls import path
from . import views

app_name = 'pomodoro'

urlpatterns = [
    # Страница выполнения конкретной задачи
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),

    # API для работы с таймером
    path('api/start_session/', views.start_session, name='start_session'),
    path('api/end_session/', views.end_session, name='end_session'),

    # История сессий
    path('sessions/', views.session_history, name='session_history'),
]