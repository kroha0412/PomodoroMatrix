# analytics/apps.py
"""
Конфигурация приложения Analytics.
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def ready(self):
        """
        Метод вызывается при загрузке приложения.
        """
        # Импортируем сигналы здесь, чтобы избежать циклических импортов
        try:
            from . import signals
        except ImportError:
            pass