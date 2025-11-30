# tasks/urls.py
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('matrix/', views.matrix_view, name='matrix'),
    path('task/create/', views.create_task, name='create_task'),
    path('task/<int:task_id>/update/', views.update_task, name='update_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/reorder/', views.reorder_tasks, name='reorder_tasks'),
]