# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('eisenhower-method/', views.eisenhower_method, name='eisenhower_method'),
    path('pomodoro-technique/', views.pomodoro_technique, name='pomodoro_technique'),
    path('methods-guide/', views.methods_guide, name='methods_guide'),  # ЭТО НАША СТРАНИЦА!
]