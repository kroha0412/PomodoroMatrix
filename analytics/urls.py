# analytics/urls.py
"""
URL-маршруты для модуля аналитики.
Только основные пути для упрощенной аналитики.
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Главная панель аналитики
    path('', views.analytics_dashboard, name='dashboard'),

    # API endpoint для динамического обновления данных (только ежедневная статистика)
    path('api/daily-stats/', views.api_daily_stats, name='api_daily_stats'),

    # УБРАЛИ: path('api/quadrant-stats/', views.api_quadrant_stats, name='api_quadrant_stats'),
]