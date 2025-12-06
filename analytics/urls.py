# analytics/urls.py
"""
URL-маршруты для модуля аналитики.
Определяет все доступные пути для просмотра статистики.
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Главная панель аналитики
    path('', views.analytics_dashboard, name='dashboard'),

    # API endpoints для динамического обновления данных
    path('api/daily-stats/', views.api_daily_stats, name='api_daily_stats'),
    path('api/quadrant-stats/', views.api_quadrant_stats, name='api_quadrant_stats'),
]