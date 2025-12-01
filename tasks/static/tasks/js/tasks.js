// tasks/static/tasks/js/tasks.js - УПРОЩЕННАЯ ВЕРСИЯ
class TaskManager {
    constructor() {
        this.init();
    }

    init() {
        console.log('TaskManager initialized');
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupModal();
    }

    setupEventListeners() {
        // Обработка формы создания задачи
        const taskForm = document.getElementById('task-form');
        if (taskForm) {
            taskForm.addEventListener('submit', (e) => this.handleCreateTask(e));
        }

        // Делегирование событий
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-edit') ||
                e.target.closest('.btn-edit')) {
                const button = e.target.classList.contains('btn-edit') ?
                              e.target : e.target.closest('.btn-edit');
                const taskId = button.dataset.taskId;
                this.handleEditTask(taskId);
            }

            if (e.target.classList.contains('btn-delete') ||
                e.target.closest('.btn-delete')) {
                const button = e.target.classList.contains('btn-delete') ?
                              e.target : e.target.closest('.btn-delete');
                const taskId = button.dataset.taskId;
                this.handleDeleteTask(taskId);
            }
        });
    }

    setupModal() {
        const modal = document.getElementById('edit-task-modal');
        const closeBtn = modal.querySelector('.close');
        const cancelBtn = document.getElementById('cancel-edit');
        const editForm = document.getElementById('edit-task-form');

        closeBtn.addEventListener('click', () => this.closeModal());
        cancelBtn.addEventListener('click', () => this.closeModal());

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        editForm.addEventListener('submit', (e) => this.handleUpdateTask(e));
    }

    setupDragAndDrop() {
        const taskCards = document.querySelectorAll('.task-card[draggable="true"]');
        const containers = document.querySelectorAll('.tasks-container, #tasks-list');

        taskCards.forEach(task => {
            task.addEventListener('dragstart', (e) => this.handleDragStart(e));
            task.addEventListener('dragend', (e) => this.handleDragEnd(e));
        });

        containers.forEach(container => {
            container.addEventListener('dragover', (e) => this.handleDragOver(e));
            container.addEventListener('drop', (e) => this.handleDrop(e));
        });
    }

    async handleCreateTask(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const createBtn = document.getElementById('create-task-btn');

        // Валидация
        const title = document.getElementById('task-title-input').value.trim();
        if (!title) {
            this.showError('title-error', 'Введите название задачи');
            return;
        }

        // Показываем loading
        const originalText = createBtn.textContent;
        createBtn.textContent = 'Создание...';
        createBtn.disabled = true;

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // Очищаем форму
                form.reset();
                this.clearErrors();

                // Показываем уведомление
                this.showNotification('Задача создана успешно!', 'success');

                // Перезагружаем страницу
                setTimeout(() => {
                    location.reload();
                }, 1000);

            } else {
                // Показываем ошибки
                this.showFormErrors(result.errors);
            }

        } catch (error) {
            console.error('Error creating task:', error);
            this.showNotification('Ошибка соединения с сервером', 'error');
        } finally {
            createBtn.textContent = originalText;
            createBtn.disabled = false;
        }
    }

    async handleEditTask(taskId) {
        try {
            const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
            if (!taskElement) {
                throw new Error('Задача не найдена');
            }

            const title = taskElement.querySelector('.task-title').textContent;
            const description = taskElement.querySelector('.task-description')?.textContent || '';

            document.getElementById('edit-task-id').value = taskId;
            document.getElementById('edit-task-title').value = title;
            document.getElementById('edit-task-description').value = description;

            this.openModal();

        } catch (error) {
            console.error('Error loading task for editing:', error);
            this.showNotification('Ошибка загрузки задачи', 'error');
        }
    }

    async handleUpdateTask(e) {
        e.preventDefault();

        const taskId = document.getElementById('edit-task-id').value;
        const title = document.getElementById('edit-task-title').value.trim();
        const description = document.getElementById('edit-task-description').value.trim();
        const saveBtn = document.getElementById('save-task-btn');

        if (!title) {
            this.showError('edit-title-error', 'Введите название задачи');
            return;
        }

        const originalText = saveBtn.textContent;
        saveBtn.textContent = 'Сохранение...';
        saveBtn.disabled = true;

        try {
            const response = await fetch(`/tasks/task/${taskId}/update/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: new URLSearchParams({
                    'title': title,
                    'description': description
                })
            });

            const result = await response.json();

            if (result.success) {
                const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskElement) {
                    taskElement.querySelector('.task-title').textContent = title;

                    const descElement = taskElement.querySelector('.task-description');
                    if (description) {
                        if (descElement) {
                            descElement.textContent = description;
                        } else {
                            const newDesc = document.createElement('p');
                            newDesc.className = 'task-description';
                            newDesc.textContent = description;
                            taskElement.appendChild(newDesc);
                        }
                    } else if (descElement) {
                        descElement.remove();
                    }
                }

                this.closeModal();
                this.showNotification('Задача обновлена', 'success');

            } else {
                this.showNotification('Ошибка обновления задачи', 'error');
            }

        } catch (error) {
            console.error('Error updating task:', error);
            this.showNotification('Ошибка обновления задачи', 'error');
        } finally {
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
        }
    }

    async handleDeleteTask(taskId) {
        if (!confirm('Удалить эту задачу?')) {
            return;
        }

        try {
            const response = await fetch(`/tasks/task/${taskId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
                if (taskElement) {
                    taskElement.remove();
                }

                this.showNotification('Задача удалена', 'success');
            } else {
                throw new Error(result.error || 'Ошибка удаления задачи');
            }

        } catch (error) {
            console.error('Error deleting task:', error);
            this.showNotification(error.message, 'error');
        }
    }

    // Drag-and-drop методы (простая версия)
    handleDragStart(e) {
        e.target.classList.add('dragging');
        e.dataTransfer.setData('text/plain', e.target.dataset.taskId);
        e.dataTransfer.effectAllowed = 'move';
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    async handleDrop(e) {
        e.preventDefault();

        const taskId = e.dataTransfer.getData('text/plain');
        const draggedTask = document.querySelector(`[data-task-id="${taskId}"]`);
        const targetContainer = e.target.closest('.tasks-container') ||
                               e.target.closest('#tasks-list');

        if (!targetContainer || !draggedTask) return;

        let quadrantId = 0;
        if (targetContainer.classList.contains('tasks-container')) {
            quadrantId = targetContainer.dataset.quadrantId;
        }

        const tasksInTarget = targetContainer.querySelectorAll('.task-card');
        const newOrder = tasksInTarget.length;

        try {
            const response = await fetch('/tasks/tasks/reorder/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    task_id: parseInt(taskId),
                    new_quadrant_id: parseInt(quadrantId),
                    new_order: newOrder
                })
            });

            const result = await response.json();

            if (result.success) {
                targetContainer.appendChild(draggedTask);
                this.showNotification('Задача перемещена', 'success');
            } else {
                throw new Error(result.error || 'Ошибка перемещения задачи');
            }

        } catch (error) {
            console.error('Error moving task:', error);
            this.showNotification(error.message, 'error');
        }
    }

    handleDragEnd(e) {
        e.target.classList.remove('dragging');
    }

    // Модальное окно
    openModal() {
        document.getElementById('edit-task-modal').style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        document.getElementById('edit-task-modal').style.display = 'none';
        document.body.style.overflow = 'auto';
        document.getElementById('edit-task-form').reset();
        this.clearEditErrors();
    }

    clearEditErrors() {
        const errorElements = document.querySelectorAll('#edit-task-form .error-message');
        errorElements.forEach(el => el.textContent = '');
    }

    showFormErrors(errors) {
        this.clearErrors();

        if (errors.title) {
            this.showError('title-error', errors.title[0]);
        }

        if (errors.__all__) {
            this.showNotification(errors.__all__[0], 'error');
        }
    }

    showError(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = message;
            element.style.color = '#dc3545';
            element.style.fontSize = '0.875rem';
            element.style.marginTop = '0.25rem';
        }
    }

    clearErrors() {
        const errorElements = document.querySelectorAll('.error-message');
        errorElements.forEach(el => el.textContent = '');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#4ECDC4' : '#FF6B6B'};
            color: white;
            border-radius: 5px;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    new TaskManager();
});