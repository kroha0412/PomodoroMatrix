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
        logger.info(
            f"[SIGNAL] Получен сигнал для PomodoroSession: создана={created}, тип={instance.session_type}, пользователь={instance.user.username}")

        # Импортируем здесь, чтобы избежать циклических импортов
        ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

        # Только для рабочих сессий и только при создании
        if created and instance.session_type == 'work':
            logger.info(f"[SIGNAL] Обрабатываем рабочую сессию для пользователя: {instance.user.username}")

            # Получаем дату сессии
            session_date = instance.start_time.date()
            logger.info(f"[SIGNAL] Дата сессии: {session_date}")

            # Получаем или создаем статистику за день
            stats, created_stats = ProductivityStats.objects.get_or_create(
                user=instance.user,
                date=session_date,
                defaults={
                    'time_spent_per_quadrant': {"1": 0, "2": 0, "3": 0, "4": 0}
                }
            )

            logger.info(f"[SIGNAL] Статистика {'создана' if created_stats else 'найдена'}: ID={stats.id}")

            # Увеличиваем счетчик Pomodoro
            stats.total_pomodoros_completed += 1
            logger.info(f"[SIGNAL] Увеличено количество Pomodoro: {stats.total_pomodoros_completed}")

            # Увеличиваем счетчик запланированных Pomodoro
            stats.planned_pomodoros += 1

            # Добавляем время в соответствующий квадрант
            if instance.task and instance.task.quadrant:
                quadrant_key = str(instance.task.quadrant.priority_order)
                current_time = stats.time_spent_per_quadrant.get(quadrant_key, 0)

                # Добавляем 25 минут (1500 секунд) за Pomodoro
                new_time = current_time + 1500
                stats.time_spent_per_quadrant[quadrant_key] = new_time

                logger.info(f"[SIGNAL] Добавлено время в квадрант {quadrant_key}: {current_time} → {new_time} секунд")

                # Если это Квадрант 2, обновляем специальное поле
                if quadrant_key == "2":
                    stats.quadrant_2_time += 1500
                    logger.info(f"[SIGNAL] Добавлено время в квадрант 2: {stats.quadrant_2_time} секунд")
            else:
                logger.info(f"[SIGNAL] Нет задачи или квадранта у сессии")

            # Пересчитываем оценки
            stats.calculate_scores()
            stats.save()

            logger.info(
                f"[SIGNAL] Статистика сохранена успешно. Продуктивность: {stats.productivity_score}, Фокус: {stats.focus_score}")

    except Exception as e:
        logger.error(f"[SIGNAL] Ошибка обновления статистики из PomodoroSession: {e}", exc_info=True)


@receiver(post_delete, sender='tasks.Task')
def handle_task_deletion(sender, instance, **kwargs):
    """
    Обрабатывает удаление задачи.
    """
    try:
        # Если задача была выполненной, уменьшаем счетчик в статистике
        if instance.status == 'completed':
            ProductivityStats = apps.get_model('analytics', 'ProductivityStats')

            # Ищем статистику за день выполнения задачи
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
        logger.error(f"[SIGNAL] Ошибка обновления статистики при удалении задачи: {e}")