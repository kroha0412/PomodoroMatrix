# tasks/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import Task, EisenhowerQuadrant
from .forms import TaskForm, TaskReorderForm


@login_required
def matrix_view(request):
    """Страница с матрицей и списком нераспределенных задач"""

    # Получаем все квадранты
    quadrants = EisenhowerQuadrant.objects.all().order_by('priority_order')

    # Получаем задачи без квадранта (еще не распределенные)
    unassigned_tasks = Task.objects.filter(
        user=request.user,
        quadrant__isnull=True,
        status='active'
    ).order_by('created_at')

    # Получаем все распределенные задачи (с квадрантами)
    tasks_with_quadrants = Task.objects.filter(
        user=request.user,
        quadrant__isnull=False,
        status='active'
    ).order_by('quadrant__priority_order', 'display_order', 'created_at')

    # Обработка POST запроса (создание задачи)
    if request.method == 'POST':
        print("POST request received")  # Для отладки
        print("POST data:", dict(request.POST))  # Для отладки

        # Используем нашу упрощенную форму
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                # Создаем задачу с обязательными полями по умолчанию
                task = form.save(commit=False)
                task.user = request.user
                task.quadrant = None  # Без квадранта при создании
                task.status = 'active'
                task.priority = 1  # Значение по умолчанию
                task.estimated_pomodoros = 1  # Значение по умолчанию
                task.completed_pomodoros = 0  # Значение по умолчанию
                task.display_order = 0  # Значение по умолчанию
                task.save()

                print(f"Task created: {task.id} - {task.title}")  # Для отладки

                return JsonResponse({
                    'success': True,
                    'task_id': task.id,
                    'message': 'Задача создана',
                    'task_title': task.title,
                    'task_description': task.description
                })

            except Exception as e:
                print(f"Error creating task: {e}")  # Для отладки
                import traceback
                traceback.print_exc()  # Печатаем полный traceback

                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': [f'Ошибка создания задачи: {str(e)}']}
                })
        else:
            print("Form errors:", form.errors)  # Для отладки
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })

    # GET запрос - просто показываем страницу
    context = {
        'quadrants': quadrants,
        'unassigned_tasks': unassigned_tasks,
        'tasks': tasks_with_quadrants,
    }

    return render(request, 'tasks/eisenhower_matrix.html', context)


@login_required
@csrf_exempt
def update_task(request, task_id):
    """Обновление задачи (редактирование названия и описания)"""
    if request.method == 'POST':
        try:
            # Получаем задачу
            task = Task.objects.get(id=task_id, user=request.user)

            # Получаем данные из POST запроса
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()

            # Валидация
            if not title:
                return JsonResponse({
                    'success': False,
                    'error': 'Название задачи обязательно'
                })

            # Обновляем данные задачи
            task.title = title
            task.description = description
            task.updated_at = timezone.now()
            task.save()

            print(f"Task updated: {task.id} - {task.title}")  # Для отладки

            return JsonResponse({
                'success': True,
                'message': 'Задача обновлена',
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description
                }
            })

        except Task.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            })
        except Exception as e:
            print(f"Error updating task: {e}")  # Для отладки
            return JsonResponse({
                'success': False,
                'error': f'Ошибка обновления задачи: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный метод запроса'
    })


@login_required
@csrf_exempt
def delete_task(request, task_id):
    """Удаление задачи"""
    if request.method == 'POST':
        try:
            task = Task.objects.get(id=task_id, user=request.user)
            task.delete()

            print(f"Task deleted: {task_id}")  # Для отладки

            return JsonResponse({'success': True})

        except Task.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            })
        except Exception as e:
            print(f"Error deleting task: {e}")  # Для отладки
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный запрос'
    })


@login_required
@csrf_exempt
def reorder_tasks(request):
    """Обработчик перетаскивания задач между квадрантами"""
    if request.method == 'POST':
        try:
            # Парсим JSON данные
            data = json.loads(request.body)
            task_id = data.get('task_id')
            new_quadrant_id = data.get('new_quadrant_id')
            new_order = data.get('new_order')

            print(
                f"Reorder request: task_id={task_id}, quadrant_id={new_quadrant_id}, order={new_order}")  # Для отладки

            task = Task.objects.get(id=task_id, user=request.user)

            # Если квадрант 0 - значит задача возвращается в нераспределенные
            if new_quadrant_id == 0:
                task.quadrant = None
                task.display_order = 0
            else:
                quadrant = EisenhowerQuadrant.objects.get(id=new_quadrant_id)
                task.quadrant = quadrant
                task.display_order = new_order

            task.save()

            print(
                f"Task reordered: {task.id} to quadrant {task.quadrant_id if task.quadrant else 'None'}")  # Для отладки

            return JsonResponse({'success': True})

        except Task.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Задача не найдена'
            })
        except EisenhowerQuadrant.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Квадрант не найден'
            })
        except Exception as e:
            print(f"Error reordering task: {e}")  # Для отладки
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({
        'success': False,
        'error': 'Неверный запрос'
    })