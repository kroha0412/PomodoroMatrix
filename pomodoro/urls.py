# pomodoro/urls.py
from django.urls import path
from . import views

app_name = 'pomodoro'

urlpatterns = [
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('api/start_session/', views.start_session, name='start_session'),
    path('api/end_session/', views.end_session, name='end_session'),
    path('task/<int:task_id>/update_progress/', views.update_task_progress, name='update_progress'),
    path('sessions/', views.session_history, name='session_history'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
]