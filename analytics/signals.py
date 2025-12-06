# analytics/signals.py
"""
Сигналы Django для автоматического обновления статистики.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


@receiver(post_save)
def handle_pomodoro_session(sender, **kwargs):
    """
    Обрабатывает сохранение Pomodoro сессии.
    """
    # Проверяем, что это PomodoroSession
    if sender.__name__ == 'PomodoroSession':
        instance = kwargs.get('instance')
        created = kwargs.get('created')

        if created and instance.session_type == 'work' and instance.status == 'completed':
            try:
                # Импортируем здесь, чтобы избежать циклических импортов
                ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

                # Получаем или создаем статистику за день
                stats, _ = ProductivityStats.objects.get_or_create(
                    user=instance.user,
                    date=instance.start_time.date(),
                    defaults={
                        'time_spent_per_quadrant': {"1": 0, "2": 0, "3": 0, "4": 0}
                    }
                )

                # Увеличиваем счетчик Pomodoro
                stats.total_pomodoros_completed += 1
                stats.save()

            except Exception as e:
                logger.error(f"Error updating stats from Pomodoro: {e}")


@receiver(post_save)
def handle_task_completion(sender, **kwargs):
    """
    Обрабатывает завершение задачи.
    """
    # Проверяем, что это Task
    if sender.__name__ == 'Task':
        instance = kwargs.get('instance')
        created = kwargs.get('created')

        if not created and instance.status == 'completed':
            try:
                # Импортируем здесь, чтобы избежать циклических импортов
                ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

                # Получаем или создаем статистику за день
                stats, _ = ProductivityStats.objects.get_or_create(
                    user=instance.user,
                    date=timezone.now().date(),
                    defaults={
                        'time_spent_per_quadrant': {"1": 0, "2": 0, "3": 0, "4": 0}
                    }
                )

                # Увеличиваем счетчик задач
                stats.total_tasks_completed += 1
                stats.save()

            except Exception as e:
                logger.error(f"Error updating stats from Task: {e}")