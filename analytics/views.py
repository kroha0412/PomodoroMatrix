# analytics/views.py
"""
Упрощенная аналитика - только самое важное.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

from .models import ProductivityStats
from .forms import AnalyticsFilterForm


@login_required
def analytics_dashboard(request):
    """
    Упрощенная панель аналитики - только ключевые метрики.
    """
    # Инициализация формы фильтрации
    form = AnalyticsFilterForm(request.GET or None)

    # Получаем диапазон дат из формы
    if form.is_valid():
        start_date, end_date = form.get_date_range()
        selected_period = form.cleaned_data.get('period', '30')
    else:
        start_date = timezone.now().date() - timedelta(days=29)
        end_date = timezone.now().date()
        selected_period = '30'

    # Получаем статистику за период
    stats = ProductivityStats.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Создаем полные данные за период
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

    # Сводная статистика за период
    summary = ProductivityStats.get_user_summary(
        user=request.user,
        days=(end_date - start_date).days + 1
    )

    # Подготовка данных для графиков
    dates = [stat.date.strftime('%d.%m') for stat in daily_stats]
    productivity_scores = [float(stat.productivity_score) for stat in daily_stats]
    focus_scores = [float(stat.focus_score) for stat in daily_stats]

    # Распределение времени по квадрантам за весь период
    quadrant_totals = {"1": 0, "2": 0, "3": 0, "4": 0}
    total_time = 0

    for stat in stats:
        if isinstance(stat.time_spent_per_quadrant, dict):
            for quadrant, time in stat.time_spent_per_quadrant.items():
                if quadrant in quadrant_totals:
                    quadrant_totals[quadrant] += time
                    total_time += time

    # Процентное распределение по квадрантам
    if total_time > 0:
        quadrant_percentages = {
            quadrant: round((time / total_time) * 100, 1)
            for quadrant, time in quadrant_totals.items()
        }
    else:
        quadrant_percentages = {"1": 0, "2": 0, "3": 0, "4": 0}

    # Идеальное распределение (рекомендация)
    ideal_distribution = {"1": 10, "2": 60, "3": 20, "4": 10}

    # Подготавливаем данные для графиков
    chart_data = {
        'daily': {
            'labels': dates if dates else ['Нет данных'],
            'productivity': productivity_scores if productivity_scores else [0],
            'focus': focus_scores if focus_scores else [0],
        },
        'quadrants': {
            'labels': ['Кв. 1', 'Кв. 2', 'Кв. 3', 'Кв. 4'],
            'data': [
                quadrant_percentages.get("1", 0),
                quadrant_percentages.get("2", 0),
                quadrant_percentages.get("3", 0),
                quadrant_percentages.get("4", 0)
            ],
            'ideal': list(ideal_distribution.values()),
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        }
    }

    # Контекст для шаблона
    context = {
        'title': 'Аналитика продуктивности',
        'form': form,
        'summary': summary,
        'chart_data': json.dumps(chart_data, ensure_ascii=False),
        'start_date': start_date,
        'end_date': end_date,
        'quadrant_percentages': quadrant_percentages,
        'quadrant_totals': quadrant_totals,
        'ideal_distribution': ideal_distribution,
        'selected_period': selected_period,
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def api_daily_stats(request):
    """
    API endpoint для получения ежедневной статистики.
    """
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    stats = ProductivityStats.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')

    dates = []
    productivity = []
    focus = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%d.%m'))
        day_stats = stats.filter(date=current_date).first()

        if day_stats:
            productivity.append(float(day_stats.productivity_score))
            focus.append(float(day_stats.focus_score))
        else:
            productivity.append(0)
            focus.append(0)

        current_date += timedelta(days=1)

    data = {
        'dates': dates,
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

    # Агрегируем время по квадрантам
    quadrant_totals = {"1": 0, "2": 0, "3": 0, "4": 0}
    for stat in stats:
        if isinstance(stat.time_spent_per_quadrant, dict):
            for quadrant, time in stat.time_spent_per_quadrant.items():
                if quadrant in quadrant_totals:
                    quadrant_totals[quadrant] += time

    total_time = sum(quadrant_totals.values())
    if total_time > 0:
        quadrant_percentages = {
            quadrant: round((time / total_time) * 100, 1)
            for quadrant, time in quadrant_totals.items()
        }
    else:
        quadrant_percentages = {"1": 0, "2": 0, "3": 0, "4": 0}

    data = {
        'labels': ['Кв. 1', 'Кв. 2', 'Кв. 3', 'Кв. 4'],
        'data': [
            quadrant_percentages.get("1", 0),
            quadrant_percentages.get("2", 0),
            quadrant_percentages.get("3", 0),
            quadrant_percentages.get("4", 0)
        ],
        'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
        'total_time': total_time,
        'total_time_formatted': f"{total_time // 3600}ч {(total_time % 3600) // 60}м"
    }

    return JsonResponse(data)