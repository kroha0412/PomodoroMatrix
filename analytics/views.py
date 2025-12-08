# analytics/views.py
"""
Упрощенная аналитика - только 3 метрики и график.
"""
from django.db.models import Sum, Avg, Count
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
    Упрощенная панель аналитики - только 3 метрики и график.
    """
    # Инициализация формы фильтрации
    form = AnalyticsFilterForm(request.GET or None)

    # Получаем диапазон дат из формы
    if form.is_valid():
        start_date, end_date = form.get_date_range()
        selected_period = form.cleaned_data.get('period', '7')
    else:
        # По умолчанию 7 дней
        start_date = timezone.now().date() - timedelta(days=6)
        end_date = timezone.now().date()
        selected_period = '7'

    # Получаем статистику за период
    stats = ProductivityStats.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('date')

    # Простая сводная статистика за период
    # УБРАЛИ: total_pomodoros - не показываем количество Pomodoro сессий
    total_tasks = stats.aggregate(total=Sum('total_tasks_completed'))['total'] or 0
    avg_productivity = stats.aggregate(avg=Avg('productivity_score'))['avg'] or 0
    avg_focus = stats.aggregate(avg=Avg('focus_score'))['avg'] or 0

    # Активные дни (дни со статистикой)
    active_days = stats.count()

    summary = {
        'total_tasks': total_tasks,
        'avg_productivity': round(avg_productivity, 1),
        'avg_focus': round(avg_focus, 1),
        'active_days': active_days,
        'total_days': (end_date - start_date).days + 1
    }

    # Подготовка данных для графиков
    dates = []
    productivity_scores = []
    focus_scores = []

    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%d.%m'))

        if day_stats := stats.filter(date=current_date).first():
            productivity_scores.append(float(day_stats.productivity_score))
            focus_scores.append(float(day_stats.focus_score))
        else:
            productivity_scores.append(0)
            focus_scores.append(0)

        current_date += timedelta(days=1)

    # Данные для графика
    chart_data = {
        'daily': {
            'labels': dates if dates else ['Нет данных'],
            'productivity': productivity_scores if productivity_scores else [0],
            'focus': focus_scores if focus_scores else [0],
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
        'selected_period': selected_period,
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def api_daily_stats(request):
    """
    API endpoint для получения ежедневной статистики.
    """
    days = int(request.GET.get('days', 7))  # По умолчанию 7 дней
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