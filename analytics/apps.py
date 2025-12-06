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
        Регистрируем сигналы.
        """
        # Импортируем сигналы здесь, чтобы они были зарегистрированы
        import analytics.signals