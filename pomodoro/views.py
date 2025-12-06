# pomodoro/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from tasks.models import Task
from users.models import UserSettings
from .models import PomodoroSession


@login_required
def task_detail(request, task_id):
    """
    Страница с Pomodoro-таймером для конкретной задачи
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)

    try:
        settings = UserSettings.objects.get(user=request.user)
    except UserSettings.DoesNotExist:
        # Создаем настройки по умолчанию, если их нет
        settings = UserSettings.objects.create(user=request.user)

    # Получаем сегодняшние сессии для этой задачи
    today = timezone.now().date()
    today_sessions = PomodoroSession.objects.filter(
        user=request.user,
        task=task,
        start_time__date=today
    ).count()

    # Последние 5 сессий
    recent_sessions = PomodoroSession.objects.filter(
        user=request.user,
        task=task
    ).order_by('-start_time')[:5]

    # Вычисляем процент выполнения
    if task.estimated_pomodoros > 0:
        progress_percentage = (task.completed_pomodoros / task.estimated_pomodoros) * 100
    else:
        progress_percentage = 0

    context = {
        'task': task,
        'settings': settings,
        'today_sessions': today_sessions,
        'recent_sessions': recent_sessions,
        'progress_percentage': progress_percentage,
    }

    return render(request, 'pomodoro/task_detail.html', context)


@login_required
@csrf_exempt
def start_session(request):
    """
    API: Начать новую Pomodoro сессию
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            session_type = data.get('session_type', 'work')

            task = Task.objects.get(id=task_id, user=request.user)

            session = PomodoroSession.objects.create(
                user=request.user,
                task=task,
                session_type=session_type,
                status='completed'
            )

            return JsonResponse({
                'success': True,
                'session_id': session.id,
                'message': f'{session.get_session_type_display()} сессия начата'
            })

        except Task.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })


@login_required
@csrf_exempt
def end_session(request):
    """
    API: Завершить Pomodoro сессию
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            status = data.get('status', 'completed')

            session = PomodoroSession.objects.get(
                id=session_id,
                user=request.user
            )

            session.status = status
            session.end_time = timezone.now()
            session.save()

            # Обновляем счётчик Pomodoro в задаче
            task_progress = None
            if session.session_type == 'work' and status == 'completed':
                task = session.task
                task.completed_pomodoros += 1
                task.save()

                # Вычисляем новый процент выполнения
                if task.estimated_pomodoros > 0:
                    progress_percentage = (task.completed_pomodoros / task.estimated_pomodoros) * 100
                else:
                    progress_percentage = 0

                task_progress = {
                    'completed': task.completed_pomodoros,
                    'total': task.estimated_pomodoros,
                    'percentage': progress_percentage
                }

            return JsonResponse({
                'success': True,
                'message': 'Сессия завершена',
                'task_progress': task_progress
            })

        except PomodoroSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Сессия не найдена'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })


@login_required
def session_history(request):
    """
    История всех Pomodoro сессий
    """
    sessions = PomodoroSession.objects.filter(
        user=request.user
    ).order_by('-start_time')[:50]

    context = {
        'sessions': sessions
    }

    return render(request, 'pomodoro/session_history.html', context)


@login_required
@csrf_exempt
def complete_task(request, task_id):
    """
    Завершить задачу (отметить как выполненную)
    """
    if request.method == 'POST':
        try:
            print(f"Completing task {task_id} for user {request.user}")  # Отладка

            task = Task.objects.get(id=task_id, user=request.user)

            # Меняем статус на выполненный
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()

            print(f"Task completed successfully: {task.id} - {task.title}")  # Отладка

            return JsonResponse({
                'success': True,
                'message': 'Задача завершена успешно!',
                'redirect_url': '/tasks/matrix/'  # Добавляем URL для редиректа
            })

        except Task.DoesNotExist:
            print(f"Task {task_id} not found for user {request.user}")  # Отладка
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            })
        except Exception as e:
            print(f"Error completing task: {e}")  # Отладка
            import traceback
            traceback.print_exc()  # Полный traceback
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })


@login_required
@csrf_exempt
def update_task_progress(request, task_id):
    """Обновление прогресса выполнения задачи (количество выполненных Pomodoro)"""
    if request.method == 'POST':
        try:
            print(f"Updating progress for task {task_id}")  # Для отладки

            task = Task.objects.get(id=task_id, user=request.user)
            completed_pomodoros = request.POST.get('completed_pomodoros')

            if completed_pomodoros:
                task.completed_pomodoros = int(completed_pomodoros)
                task.save()
                print(f"Task {task_id} progress updated to {task.completed_pomodoros}")

            return JsonResponse({
                'success': True,
                'message': 'Прогресс обновлен',
                'progress': {
                    'completed': task.completed_pomodoros,
                    'estimated': task.estimated_pomodoros,
                    'percentage': (
                                task.completed_pomodoros / task.estimated_pomodoros * 100) if task.estimated_pomodoros > 0 else 0
                }
            })

        except Task.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            })
        except Exception as e:
            print(f"Error updating progress: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })