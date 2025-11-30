async moveTaskToQuadrant(targetContainer) {
    // СОХРАНЯЕМ draggedTask в локальную переменную перед асинхронной операцией
    const draggedTask = this.draggedTask;
    const taskId = draggedTask.dataset.taskId;
    const newQuadrantId = targetContainer.id.replace('quadrant-', '');
    
    console.log('Перемещение задачи:', { taskId, newQuadrantId, draggedTask });
    
    const tasksInTarget = targetContainer.querySelectorAll('.task-card');
    const newOrder = tasksInTarget.length;
    
    try {
        const response = await fetch('/tasks/tasks/reorder/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: new URLSearchParams({
                'task_id': taskId,
                'new_quadrant_id': newQuadrantId,
                'new_order': newOrder
            })
        });

        console.log('Статус ответа:', response.status);
        
        const result = await response.json();
        console.log('Результат:', result);
        
        if (result.success) {
            // Используем локальную переменную вместо this.draggedTask
            targetContainer.appendChild(draggedTask);
            this.showNotification('Задача перемещена', 'success');
        } else {
            console.error('Ошибка от сервера:', result.errors);
            throw new Error('Ошибка перемещения задачи');
        }
    } catch (error) {
        console.error('Полная ошибка перемещения задачи:', error);
        this.showNotification('Ошибка перемещения задачи', 'error');
    }
}

handleDragEnd(e) {
    // Очищаем draggedTask только после завершения всех операций
    setTimeout(() => {
        if (this.draggedTask) {
            this.draggedTask.classList.remove('dragging');
            this.draggedTask = null;
        }
        this.removeDropZoneHighlight();
    }, 100);
}