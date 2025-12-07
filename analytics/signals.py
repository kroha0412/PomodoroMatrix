# analytics/signals.py
"""
Сигналы Django для автоматического обновления статистики.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='tasks.Task')
def handle_task_completion(sender, instance, created, **kwargs):
    """
    Обрабатывает сохранение/обновление задачи.
    Обновляет статистику, когда задача помечается как выполненная.
    """
    try:
        # Импортируем здесь, чтобы избежать циклических импортов
        ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

        # Только если задача была помечена как выполненная
        if instance.status == 'completed' and not created:
            # Получаем или создаем статистику за сегодня
            today = timezone.now().date()
            stats, _ = ProductivityStats.objects.get_or_create(
                user=instance.user,
                date=today,
                defaults={
                    'time_spent_per_quadrant': {"1": 0, "2": 0, "3": 0, "4": 0}
                }
            )

            # Увеличиваем счетчик выполненных задач
            stats.total_tasks_completed += 1

            # Проверяем, выполнена ли задача в срок
            if instance.due_date and instance.completed_at:
                if instance.completed_at <= instance.due_date:
                    stats.completed_on_time_tasks += 1

            # Пересчитываем оценки
            stats.calculate_scores()
            stats.save()

            logger.info(f"Статистика обновлена для задачи: {instance.title}")

    except Exception as e:
        logger.error(f"Ошибка обновления статистики из Task: {e}")


@receiver(post_save, sender='pomodoro.PomodoroSession')
def handle_pomodoro_session(sender, instance, created, **kwargs):
    """
    Обрабатывает сохранение Pomodoro сессии.
    """
    try:
        # ПРОВЕРЯЕМ: это новая рабочая сессия?
        if created and instance.session_type == 'work':
            # Импортируем модель
            ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

            # Получаем дату сессии
            session_date = instance.start_time.date()

            # Получаем пользователя
            user = instance.user

            # Получаем или создаем статистику за день
            stats, stats_created = ProductivityStats.objects.get_or_create(
                user=user,
                date=session_date,
                defaults={
                    'time_spent_per_quadrant': {"1": 0, "2": 0, "3": 0, "4": 0}
                }
            )

            # ВАЖНОЕ ИСПРАВЛЕНИЕ: Увеличиваем счетчик Pomodoro
            stats.total_pomodoros_completed += 1

            # Устанавливаем запланированные pomodoro
            if stats.planned_pomodoros < stats.total_pomodoros_completed:
                stats.planned_pomodoros = stats.total_pomodoros_completed

            # Добавляем время в квадрант
            if instance.task and instance.task.quadrant:
                quadrant_key = str(instance.task.quadrant.priority_order)
                current_time = stats.time_spent_per_quadrant.get(quadrant_key, 0)

                # 25 минут = 1500 секунд
                stats.time_spent_per_quadrant[quadrant_key] = current_time + 1500

                # Если это Квадрант 2
                if quadrant_key == "2":
                    stats.quadrant_2_time += 1500

            # Пересчитываем оценки
            stats.calculate_scores()

            # Сохраняем
            stats.save()

            logger.info(f"Pomodoro сессия добавлена: всего {stats.total_pomodoros_completed} за {session_date}")

    except Exception as e:
        logger.error(f"Ошибка обновления статистики из PomodoroSession: {e}")


@receiver(post_delete, sender='tasks.Task')
def handle_task_deletion(sender, instance, **kwargs):
    """
    Обрабатывает удаление задачи.
    """
    try:
        if instance.status == 'completed':
            ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

            if instance.completed_at:
                stats = ProductivityStats.objects.filter(
                    user=instance.user,
                    date=instance.completed_at.date()
                ).first()

                if stats and stats.total_tasks_completed > 0:
                    stats.total_tasks_completed -= 1
                    stats.calculate_scores()
                    stats.save()

    except Exception as e:
        logger.error(f"Ошибка при удалении задачи: {e}")