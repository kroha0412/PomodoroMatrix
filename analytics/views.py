# analytics/views.py
"""
Представления (views) для модуля аналитики.
Обрабатывают запросы и отображают статистику продуктивности.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import ProductivityStats
from .forms import AnalyticsFilterForm


@login_required
def analytics_dashboard(request):
    """
    Главная панель аналитики.
    Отображает сводную статистику, графики и метрики продуктивности.
    """

    # Инициализируем форму фильтрации
    form = AnalyticsFilterForm(request.GET or None)

    # Отладочная информация
    print(f"=== ANALYTICS DEBUG ===")
    print(f"Request GET: {request.GET}")
    print(f"Form is valid: {form.is_valid()}")

    # Получаем диапазон дат из формы
    if form.is_valid():
        start_date, end_date = form.get_date_range()
        selected_period = form.cleaned_data.get('period', '30')
        print(f"Selected period: {selected_period}")
    else:
        start_date = timezone.now().date() - timedelta(days=29)
        end_date = timezone.now().date()
        selected_period = '30'
        print(f"Using default period: {selected_period}")

    print(f"Date range: {start_date} - {end_date}")

    # Если выбран "сегодня", показываем только сегодняшний день
    if selected_period == 'today':
        daily_stats = []
        today_stats = ProductivityStats.objects.filter(
            user=request.user,
            date=timezone.now().date()
        ).first()

        if today_stats:
            daily_stats.append(today_stats)
            print(f"Found today's stats: {today_stats}")
        else:
            # Если нет статистики за сегодня, создаем пустую
            daily_stats.append(ProductivityStats(
                user=request.user,
                date=timezone.now().date(),
                time_spent_per_quadrant={"1": 0, "2": 0, "3": 0, "4": 0}
            ))
            print("Created empty stats for today")
    else:
        # Получаем статистику за период
        stats = ProductivityStats.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')

        print(f"Found {stats.count()} stats records for period")

        # Заполняем пропущенные дни нулевыми значениями
        daily_stats = []
        current_date = start_date
        while current_date <= end_date:
            day_stats = stats.filter(date=current_date).first()
            if day_stats:
                daily_stats.append(day_stats)
            else:
                daily_stats.append(ProductivityStats(
                    user=request.user,
                    date=current_date,
                    time_spent_per_quadrant={"1": 0, "2": 0, "3": 0, "4": 0}
                ))
            current_date += timedelta(days=1)

        print(f"Created {len(daily_stats)} days in daily_stats")

    # Сводная статистика
    days_count = (end_date - start_date).days + 1
    summary = ProductivityStats.get_user_summary(
        user=request.user,
        days=days_count
    )

    print(f"Summary stats: {summary}")

    # Подготавливаем данные для графиков
    dates = [stat.date.strftime('%d.%m') for stat in daily_stats]
    pomodoros = [stat.total_pomodoros_completed for stat in daily_stats]
    tasks = [stat.total_tasks_completed for stat in daily_stats]
    productivity_scores = [float(stat.productivity_score) for stat in daily_stats]
    focus_scores = [float(stat.focus_score) for stat in daily_stats]

    print(f"Dates for chart: {dates}")
    print(f"Productivity scores: {productivity_scores}")
    print(f"Focus scores: {focus_scores}")

    # Распределение по квадрантам
    quadrant_totals = {"1": 0, "2": 0, "3": 0, "4": 0}
    for stat in daily_stats:
        if isinstance(stat.time_spent_per_quadrant, dict):
            for quadrant, time in stat.time_spent_per_quadrant.items():
                if quadrant in quadrant_totals:
                    quadrant_totals[quadrant] += time

    total_time = sum(quadrant_totals.values())
    if total_time > 0:
        quadrant_percentages = {
            "1": round((quadrant_totals["1"] / total_time) * 100, 1),
            "2": round((quadrant_totals["2"] / total_time) * 100, 1),
            "3": round((quadrant_totals["3"] / total_time) * 100, 1),
            "4": round((quadrant_totals["4"] / total_time) * 100, 1),
        }
    else:
        quadrant_percentages = {"1": 0, "2": 0, "3": 0, "4": 0}

    print(f"Quadrant percentages: {quadrant_percentages}")
    print(f"Quadrant totals: {quadrant_totals}")

    # Данные для графиков - УБЕДИТЕСЬ что данные не пустые!
    chart_data = {
        'daily': {
            'labels': dates if dates else ['Нет данных'],
            'productivity': productivity_scores if productivity_scores else [0],
            'focus': focus_scores if focus_scores else [0],
            'pomodoros': pomodoros if pomodoros else [0],
            'tasks': tasks if tasks else [0],
        },
        'quadrants': {
            'labels': ['Важные/Срочные', 'Важные/Несрочные', 'Неважные/Срочные', 'Неважные/Несрочные'],
            'data': [
                quadrant_percentages.get("1", 0),
                quadrant_percentages.get("2", 0),
                quadrant_percentages.get("3", 0),
                quadrant_percentages.get("4", 0)
            ],
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        }
    }

    print(f"Chart data prepared: {json.dumps(chart_data, indent=2)}")

    # Контекст для шаблона
    context = {
        'title': 'Аналитика продуктивности',
        'form': form,
        'daily_stats': daily_stats,
        'summary': summary,
        'chart_data': json.dumps(chart_data, ensure_ascii=False),  # ensure_ascii=False для кириллицы
        'start_date': start_date,
        'end_date': end_date,
        'today': timezone.now().date(),
        'quadrant_analysis': {
            'total_time': round(total_time / 3600, 1),
            'quadrant_percentages': quadrant_percentages,
            'quadrant_totals': quadrant_totals,
        }
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def api_daily_stats(request):
    """
    API endpoint для получения ежедневной статистики.
    Используется для AJAX запросов и обновления графиков.
    """

    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    stats = ProductivityStats.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Создаем данные для всех дней
    dates = []
    pomodoros = []
    tasks = []
    productivity = []
    focus = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%d.%m'))
        day_stats = stats.filter(date=current_date).first()

        if day_stats:
            pomodoros.append(day_stats.total_pomodoros_completed)
            tasks.append(day_stats.total_tasks_completed)
            productivity.append(float(day_stats.productivity_score))
            focus.append(float(day_stats.focus_score))
        else:
            pomodoros.append(0)
            tasks.append(0)
            productivity.append(0)
            focus.append(0)

        current_date += timedelta(days=1)

    data = {
        'dates': dates,
        'pomodoros': pomodoros,
        'tasks': tasks,
        'productivity': productivity,
        'focus': focus,
    }

    return JsonResponse(data)


@login_required
def api_quadrant_stats(request):
    """
    API endpoint для получения статистики по квадрантам.
    """

    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    stats = ProductivityStats.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )

    # Суммируем время по квадрантам
    quadrant_totals = {"1": 0, "2": 0, "3": 0, "4": 0}
    for stat in stats:
        if isinstance(stat.time_spent_per_quadrant, dict):
            for quadrant, time in stat.time_spent_per_quadrant.items():
                if quadrant in quadrant_totals:
                    quadrant_totals[quadrant] += time

    total_time = sum(quadrant_totals.values())

    if total_time > 0:
        percentages = {
            quadrant: round((time / total_time) * 100, 1)
            for quadrant, time in quadrant_totals.items()
        }
    else:
        percentages = {"1": 0, "2": 0, "3": 0, "4": 0}

    data = {
        'labels': ['Кв. 1', 'Кв. 2', 'Кв. 3', 'Кв. 4'],
        'data': list(percentages.values()),
        'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        'total_hours': round(total_time / 3600, 1),
    }

    return JsonResponse(data)