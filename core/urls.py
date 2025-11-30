# core/urls.py
# Импортируем функцию path для создания URL-маршрутов
from django.urls import path

# Импортируем модуль views из текущего каталога (файл views.py в той же папке)
# views содержит функции, которые будут обрабатывать запросы
from . import views

# app_name помогает избежать конфликтов имен URL между приложениями
# Это пространство имен для URL данного приложения
app_name = 'core'

# urlpatterns - список всех URL-маршрутов этого приложения
# Django проходит по этому списку сверху вниз и использует первое совпадение
urlpatterns = [
    # path('URL-адрес/', views.функция_представления, name='имя_для_шаблонов')

    # Главная страница - http://127.0.0.1:8000/
    # '' - пустая строка означает корневой URL приложения
    # views.home - функция home из файла views.py
    # name='home' - уникальное имя для этого URL (используется в шаблонах)
    path('', views.home, name='home'),

    # Страница "О проекте" - http://127.0.0.1:8000/about/
    # 'about/' - URL путь для страницы о проекте
    # views.about - функция about из файла views.py
    # name='about' - имя для использования в шаблонах
    path('about/', views.about, name='about'),

    # Страница обучения матрице Эйзенхауэра - http://127.0.0.1:8000/eisenhower-method/
    # 'eisenhower-method/' - URL путь для страницы обучения
    # views.eisenhower_method - функция eisenhower_method из views.py
    # name='eisenhower_method' - имя для шаблонов
    path('eisenhower-method/', views.eisenhower_method, name='eisenhower_method'),

    # Страница обучения методу Pomodoro - http://127.0.0.1:8000/pomodoro-technique/
    # 'pomodoro-technique/' - URL путь для страницы обучения Pomodoro
    # views.pomodoro_technique - функция pomodoro_technique из views.py
    # name='pomodoro_technique' - имя для шаблонов
    path('pomodoro-technique/', views.pomodoro_technique, name='pomodoro_technique'),
]