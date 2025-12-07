# analytics/apps.py - должно быть:

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'

    def ready(self):
        """
        Метод вызывается при загрузке приложения.
        Регистрируем сигналы.
        """
        import analytics.signals  # ЭТА СТРОКА ДОЛЖНА БЫТЬ