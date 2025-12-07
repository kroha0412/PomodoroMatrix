# analytics/urls.py
"""
URL-маршруты для модуля аналитики.
"""

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Главная панель аналитики
    path('', views.analytics_dashboard, name='dashboard'),

    # API endpoint для ежедневной статистики
    path('api/daily-stats/', views.api_daily_stats, name='api_daily_stats'),
]