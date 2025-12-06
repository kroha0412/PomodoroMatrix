from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
import json


class ProductivityStats(models.Model):
    """
    Модель для хранения ежедневной статистики продуктивности пользователей.
    Содержит агрегированные данные для построения графиков и отчетов.
    """

    # Связь "многие-к-одному" с моделью User
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    # Дата статистики
    date = models.DateField(auto_now_add=True, verbose_name="Дата статистики")

    # Основные метрики
    total_pomodoros_completed = models.PositiveIntegerField(default=0, verbose_name="Всего завершено Pomodoro")
    total_tasks_completed = models.PositiveIntegerField(default=0, verbose_name="Всего завершено задач")

    # Время по квадрантам
    time_spent_per_quadrant = models.JSONField(default=dict, verbose_name="Время по квадрантам (JSON)")
    quadrant_2_time = models.PositiveIntegerField(default=0, verbose_name="Время для Квадранта 2 (сек)")

    # Планирование и выполнение
    planned_pomodoros = models.PositiveIntegerField(default=0, verbose_name="Запланировано Pomodoro")
    completed_on_time_tasks = models.PositiveIntegerField(default=0, verbose_name="Задачи выполненные в срок")

    # Оценки
    focus_score = models.FloatField(default=0, verbose_name="Оценка фокуса (0-100)")
    productivity_score = models.FloatField(default=0, verbose_name="Оценка продуктивности (0-100)")

    # Прерывания
    interruptions_count = models.PositiveIntegerField(default=0, verbose_name="Количество прерываний")

    class Meta:
        verbose_name = "Статистика продуктивности"
        verbose_name_plural = "Статистика продуктивности"
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Статистика {self.user.username} за {self.date}"

    # ============ СВОЙСТВА (PROPERTIES) ============

    @property
    def total_time_spent(self):
        """Общее время работы за день (в секундах)"""
        if isinstance(self.time_spent_per_quadrant, dict):
            return sum(self.time_spent_per_quadrant.values())
        return 0

    @property
    def formatted_total_time(self):
        """Общее время в формате ЧЧ:ММ:СС"""
        total_seconds = self.total_time_spent
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def quadrant_distribution_percent(self):
        """Распределение времени по квадрантам в процентах"""
        total = self.total_time_spent
        if total == 0:
            return {"1": 0, "2": 0, "3": 0, "4": 0}

        distribution = {}
        quadrants = self.time_spent_per_quadrant

        # Убедимся, что у нас есть все квадранты
        for i in range(1, 5):
            quadrant_key = str(i)
            time_seconds = quadrants.get(quadrant_key, 0)
            distribution[quadrant_key] = round((time_seconds / total) * 100, 1)

        return distribution

    @property
    def quadrant_2_percentage(self):
        """Процент времени, потраченного на Квадрант 2"""
        total = self.total_time_spent
        if total == 0:
            return 0
        return round((self.quadrant_2_time / total) * 100, 1)

    @property
    def pomodoro_efficiency(self):
        """Эффективность Pomodoro (выполненные/запланированные)"""
        if self.planned_pomodoros == 0:
            return 0
        return round((self.total_pomodoros_completed / self.planned_pomodoros) * 100, 1)

    @property
    def task_completion_rate(self):
        """Процент выполненных вовремя задач"""
        if self.total_tasks_completed == 0:
            return 0
        return round((self.completed_on_time_tasks / self.total_tasks_completed) * 100, 1)

    @property
    def focus_efficiency(self):
        """Эффективность фокуса"""
        return round(self.focus_score, 1)

    @property
    def quadrant_names(self):
        """Названия квадрантов для отображения"""
        return {
            "1": "Важные/Срочные",
            "2": "Важные/Несрочные",
            "3": "Неважные/Срочные",
            "4": "Неважные/Несрочные"
        }

    @property
    def quadrant_colors(self):
        """Цвета для квадрантов (совпадают с матрицей)"""
        return {
            "1": "#FF6B6B",  # Красный
            "2": "#4ECDC4",  # Бирюзовый
            "3": "#45B7D1",  # Голубой
            "4": "#96CEB4"  # Зеленый
        }

    # ============ МЕТОДЫ КЛАССА ============

    @classmethod
    def get_or_create_daily_stats(cls, user, date=None):
        """Получить или создать статистику за день"""
        if date is None:
            date = timezone.now().date()

        try:
            return cls.objects.get(user=user, date=date)
        except cls.DoesNotExist:
            # Создаем новую запись с базовой структурой
            return cls.objects.create(
                user=user,
                date=date,
                time_spent_per_quadrant={"1": 0, "2": 0, "3": 0, "4": 0}
            )

    @classmethod
    def get_user_daily_stats(cls, user, days=30):
        """Получить дневную статистику за период"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)

        stats = cls.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Заполняем пропущенные дни нулевыми значениями
        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)

        stats_dict = {stat.date: stat for stat in stats}
        complete_stats = []

        for date in all_dates:
            if date in stats_dict:
                complete_stats.append(stats_dict[date])
            else:
                complete_stats.append(cls(
                    user=user,
                    date=date,
                    time_spent_per_quadrant={"1": 0, "2": 0, "3": 0, "4": 0}
                ))

        return complete_stats

    @classmethod
    def get_user_summary(cls, user, days=30):
        """Сводная статистика за период"""
        stats = cls.objects.filter(
            user=user,
            date__gte=timezone.now().date() - timedelta(days=days)
        )

        if not stats.exists():
            return {
                'total_days': 0,
                'active_days': 0,
                'total_pomodoros': 0,
                'total_tasks': 0,
                'avg_productivity': 0,
                'avg_focus': 0,
                'total_interruptions': 0,
                'quadrant_distribution': {"1": 0, "2": 0, "3": 0, "4": 0},
                'pomodoro_efficiency': 0,
                'task_completion_rate': 0,
                'avg_quadrant_2_time': 0
            }

        # Подсчитываем активные дни (дни с работой)
        active_days = stats.filter(total_time_spent__gt=0).count()

        # Агрегированные данные
        aggregates = stats.aggregate(
            total_pomodoros=Sum('total_pomodoros_completed'),
            total_tasks=Sum('total_tasks_completed'),
            avg_productivity=Avg('productivity_score'),
            avg_focus=Avg('focus_score'),
            total_interruptions=Sum('interruptions_count'),
            total_quadrant_2=Sum('quadrant_2_time')
        )

        # Распределение по квадрантам
        quadrant_totals = {"1": 0, "2": 0, "3": 0, "4": 0}
        for stat in stats:
            for quadrant, time in stat.time_spent_per_quadrant.items():
                if quadrant in quadrant_totals:
                    quadrant_totals[quadrant] += time

        total_time = sum(quadrant_totals.values())
        if total_time > 0:
            quadrant_distribution = {
                quadrant: round((time / total_time) * 100, 1)
                for quadrant, time in quadrant_totals.items()
            }
        else:
            quadrant_distribution = {"1": 0, "2": 0, "3": 0, "4": 0}

        # Эффективность
        total_planned = stats.aggregate(Sum('planned_pomodoros'))['planned_pomodoros__sum'] or 0
        pomodoro_efficiency = 0
        if total_planned > 0:
            pomodoro_efficiency = round((aggregates['total_pomodoros'] or 0) / total_planned * 100, 1)

        # Процент задач в срок
        total_completed_tasks = aggregates['total_tasks'] or 0
        completed_on_time = stats.aggregate(Sum('completed_on_time_tasks'))['completed_on_time_tasks__sum'] or 0
        task_completion_rate = 0
        if total_completed_tasks > 0:
            task_completion_rate = round(completed_on_time / total_completed_tasks * 100, 1)

        # Среднее время в Квадранте 2
        avg_quadrant_2_time = 0
        if active_days > 0:
            avg_quadrant_2_time = round((aggregates['total_quadrant_2'] or 0) / active_days / 60, 1)  # в минутах

        return {
            'total_days': days,
            'active_days': active_days,
            'total_pomodoros': aggregates['total_pomodoros'] or 0,
            'total_tasks': aggregates['total_tasks'] or 0,
            'avg_productivity': round(aggregates['avg_productivity'] or 0, 1),
            'avg_focus': round(aggregates['avg_focus'] or 0, 1),
            'total_interruptions': aggregates['total_interruptions'] or 0,
            'quadrant_distribution': quadrant_distribution,
            'pomodoro_efficiency': pomodoro_efficiency,
            'task_completion_rate': task_completion_rate,
            'avg_quadrant_2_time': avg_quadrant_2_time,
            'quadrant_2_percentage': quadrant_distribution.get("2", 0)
        }

    @classmethod
    def get_weekly_stats(cls, user, weeks=4):
        """Статистика по неделям"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=weeks * 7)

        stats = cls.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')

        # Группируем по неделям
        weekly_data = {}
        for stat in stats:
            week_start = stat.date - timedelta(days=stat.date.weekday())
            week_key = week_start.strftime('%d.%m')

            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'pomodoros': 0,
                    'tasks': 0,
                    'productivity': [],
                    'focus': [],
                    'quadrant_time': {"1": 0, "2": 0, "3": 0, "4": 0}
                }

            weekly_data[week_key]['pomodoros'] += stat.total_pomodoros_completed
            weekly_data[week_key]['tasks'] += stat.total_tasks_completed
            weekly_data[week_key]['productivity'].append(stat.productivity_score)
            weekly_data[week_key]['focus'].append(stat.focus_score)

            for quadrant, time in stat.time_spent_per_quadrant.items():
                if quadrant in weekly_data[week_key]['quadrant_time']:
                    weekly_data[week_key]['quadrant_time'][quadrant] += time

        # Вычисляем средние значения для недель
        for week in weekly_data.values():
            if week['productivity']:
                week['avg_productivity'] = round(sum(week['productivity']) / len(week['productivity']), 1)
                week['avg_focus'] = round(sum(week['focus']) / len(week['focus']), 1)
            else:
                week['avg_productivity'] = 0
                week['avg_focus'] = 0

            del week['productivity']
            del week['focus']

        return weekly_data

    # ============ МЕТОДЫ ДЛЯ ОБНОВЛЕНИЯ ДАННЫХ ============

    def add_pomodoro_session(self, task=None, session_type='work'):
        """Добавить завершенную Pomodoro сессию"""
        self.total_pomodoros_completed += 1

        if task and task.quadrant:
            # Увеличиваем время в соответствующем квадранте
            quadrant_key = str(task.quadrant.priority_order)
            current_time = self.time_spent_per_quadrant.get(quadrant_key, 0)

            # Добавляем 25 минут (1500 секунд) за Pomodoro
            self.time_spent_per_quadrant[quadrant_key] = current_time + 1500

            # Если это Квадрант 2, обновляем специальное поле
            if quadrant_key == "2":
                self.quadrant_2_time += 1500

        self.calculate_scores()
        self.save()

    def add_completed_task(self, task, on_time=True):
        """Добавить завершенную задачу"""
        self.total_tasks_completed += 1
        if on_time:
            self.completed_on_time_tasks += 1

        self.calculate_scores()
        self.save()

    def add_interruption(self):
        """Добавить прерывание"""
        self.interruptions_count += 1

        # Прерывания снижают оценку фокуса
        if self.focus_score > 10:
            self.focus_score -= 5

        self.save()

    def calculate_scores(self):
        """Автоматически рассчитать оценки продуктивности и фокуса"""
        # Рассчитываем оценку продуктивности (0-100)
        # Основана на: выполненных задачах, эффективности Pomodoro, времени в Квадранте 2

        task_score = min(self.total_tasks_completed * 20, 40)  # до 40 баллов за задачи
        pomodoro_score = min(self.pomodoro_efficiency * 0.3, 30)  # до 30 баллов за эффективность Pomodoro
        quadrant_2_score = min(self.quadrant_2_percentage * 0.3, 30)  # до 30 баллов за время в Квадранте 2

        self.productivity_score = round(task_score + pomodoro_score + quadrant_2_score, 1)

        # Рассчитываем оценку фокуса (0-100)
        # Основана на: количестве прерываний, эффективности Pomodoro

        base_focus = 80
        interruption_penalty = min(self.interruptions_count * 5, 40)  # штраф за прерывания
        efficiency_bonus = min(self.pomodoro_efficiency * 0.2, 20)  # бонус за эффективность

        self.focus_score = round(max(0, base_focus - interruption_penalty + efficiency_bonus), 1)
        self.focus_score = min(self.focus_score, 100)  # Не больше 100

    def reset_daily_stats(self):
        """Сбросить статистику за день (для тестирования)"""
        self.total_pomodoros_completed = 0
        self.total_tasks_completed = 0
        self.time_spent_per_quadrant = {"1": 0, "2": 0, "3": 0, "4": 0}
        self.quadrant_2_time = 0
        self.planned_pomodoros = 0
        self.completed_on_time_tasks = 0
        self.focus_score = 0
        self.productivity_score = 0
        self.interruptions_count = 0
        self.save()