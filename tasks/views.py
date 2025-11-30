# tasks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Task, EisenhowerQuadrant
from .forms import TaskForm, TaskReorderForm


@login_required
def matrix_view(request):
    """
    Основное представление матрицы Эйзенхауэра
    """
    # Получаем все квадранты
    quadrants = EisenhowerQuadrant.objects.all().order_by('priority_order')

    # Получаем задачи пользователя, сгруппированные по квадрантам
    tasks_by_quadrant = {}
    for quadrant in quadrants:
        tasks = Task.objects.filter(
            user=request.user,
            quadrant=quadrant,
            status='active'
        ).order_by('display_order', 'priority', 'created_at')
        tasks_by_quadrant[quadrant.id] = tasks

    # Форма для создания новой задачи
    task_form = TaskForm()

    context = {
        'quadrants': quadrants,
        'tasks_by_quadrant': tasks_by_quadrant,
        'task_form': task_form,
    }

    return render(request, 'tasks/eisenhower_matrix.html', context)


@login_required
@require_http_methods(["POST"])
def create_task(request):
    """
    Создание новой задачи
    """
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'quadrant_id': task.quadrant.id
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


@login_required
@require_http_methods(["POST"])
def update_task(request, task_id):
    """
    Обновление задачи
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


@login_required
@require_http_methods(["POST"])
def delete_task(request, task_id):
    """
    Удаление задачи
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def reorder_tasks(request):
    """
    Перемещение задачи между квадрантами и изменение порядка
    """
    form = TaskReorderForm(request.POST)
    if form.is_valid():
        task_id = form.cleaned_data['task_id']
        new_quadrant_id = form.cleaned_data['new_quadrant_id']
        new_order = form.cleaned_data['new_order']

        task = get_object_or_404(Task, id=task_id, user=request.user)
        new_quadrant = get_object_or_404(EisenhowerQuadrant, id=new_quadrant_id)

        # Обновляем квадрант и порядок
        task.quadrant = new_quadrant
        task.display_order = new_order
        task.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })


@login_required
@require_http_methods(["POST"])
def complete_task(request, task_id):
    """
    Отметка задачи как выполненной
    """
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.status = 'completed'
    task.save()
    return JsonResponse({'success': True})