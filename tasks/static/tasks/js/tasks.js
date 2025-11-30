// tasks/static/tasks/js/tasks.js
class TaskManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupModal();
    }

    setupEventListeners() {
        // Кнопка показа формы создания задачи
        document.getElementById('show-task-form-btn')?.addEventListener('click', () => {
            this.toggleTaskForm();
        });

        document.getElementById('cancel-task-form')?.addEventListener('click', () => {
            this.toggleTaskForm(false);
        });

        // Форма создания задачи
        document.getElementById('task-form')?.addEventListener('submit', (e) => {
            this.handleCreateTask(e);
        });

        // Обработчики для кнопок действий с задачами
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-edit')) {
                this.handleEditTask(e.target.dataset.taskId);
            } else if (e.target.classList.contains('btn-delete')) {
                this.handleDeleteTask(e.target.dataset.taskId);
            } else if (e.target.classList.contains('btn-complete')) {
                this.handleCompleteTask(e.target.dataset.taskId);
            }
        });
    }

    setupModal() {
        const modal = document.getElementById('edit-task-modal');
        const closeBtn = modal.querySelector('.close');
        const cancelBtn = document.getElementById('cancel-edit');

        // Закрытие модального окна
        closeBtn.addEventListener('click', () => this.closeModal());
        cancelBtn.addEventListener('click', () => this.closeModal());

        // Закрытие при клике вне модального окна
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Форма редактирования
        document.getElementById('edit-task-form').addEventListener('submit', (e) => {
            this.handleUpdateTask(e);
        });
    }

    toggleTaskForm(show = true) {
        const formContainer = document.getElementById('task-form-container');
        const showBtn = document.getElementById('show-task-form-btn');

        if (show) {
            formContainer.style.display = 'block';
            showBtn.style.display = 'none';
        } else {
            formContainer.style.display = 'none';
            showBtn.style.display = 'block';
            document.getElementById('task-form').reset();
        }
    }

    async handleCreateTask(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.addTaskToDOM(result.task_id, result.quadrant_id, formData);
                form.reset();
                this.toggleTaskForm(false);
                this.showNotification('Задача создана успешно!', 'success');
            } else {
                this.showFormErrors(form, result.errors);
            }
        } catch (error) {
            console.error('Ошибка создания задачи:', error);
            this.showNotification('Ошибка создания задачи', 'error');
        }
    }

    addTaskToDOM(taskId, quadrantId, formData) {
        const quadrantContainer = document.getElementById(`quadrant-${quadrantId}`);
        const taskCard = this.createTaskCard(taskId, formData);

        quadrantContainer.querySelector('.empty-state')?.remove();
        quadrantContainer.appendChild(taskCard);
    }

    createTaskCard(taskId, formData) {
        const taskCard = document.createElement('div');
        taskCard.className = 'task-card';
        taskCard.dataset.taskId = taskId;
        taskCard.draggable = true;

        taskCard.innerHTML = `
            <div class="task-header">
                <h4 class="task-title">${formData.get('title')}</h4>
                <div class="task-actions">
                    <button class="btn-edit" data-task-id="${taskId}">✏️</button>
                    <button class="btn-delete" data-task-id="${taskId}">🗑️</button>
                    <button class="btn-complete" data-task-id="${taskId}">✅</button>
                </div>
            </div>
            ${formData.get('description') ? `<p class="task-description">${formData.get('description')}</p>` : ''}
            <div class="task-meta">
                <span class="task-priority">Приоритет: ${formData.get('priority')}</span>
                <span class="task-pomodoros">🍅 ${formData.get('estimated_pomodoros')}</span>
                ${formData.get('due_date') ? `<span class="task-due-date">📅 ${new Date(formData.get('due_date')).toLocaleDateString()}</span>` : ''}
            </div>
        `;

        return taskCard;
    }

    async handleEditTask(taskId) {
        try {
            // Получаем данные задачи (в реальном приложении нужно сделать API endpoint)
            const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
            const taskData = this.extractTaskData(taskElement);

            this.populateEditForm(taskId, taskData);
            this.openModal();
        } catch (error) {
            console.error('Ошибка редактирования задачи:', error);
            this.showNotification('Ошибка загрузки данных задачи', 'error');
        }
    }

    extractTaskData(taskElement) {
        return {
            title: taskElement.querySelector('.task-title').textContent,
            description: taskElement.querySelector('.task-description')?.textContent || '',
            quadrant: taskElement.closest('.tasks-container').id.replace('quadrant-', ''),
            priority: taskElement.querySelector('.task-priority').textContent.replace('Приоритет: ', ''),
            pomodoros: taskElement.querySelector('.task-pomodoros').textContent.replace('🍅 ', '')
        };
    }

    populateEditForm(taskId, taskData) {
        document.getElementById('edit-task-id').value = taskId;
        document.getElementById('edit-task-title').value = taskData.title;
        document.getElementById('edit-task-description').value = taskData.description;
        document.getElementById('edit-task-quadrant').value = taskData.quadrant;
        document.getElementById('edit-task-priority').value = taskData.priority;
        document.getElementById('edit-task-pomodoros').value = taskData.pomodoros;
    }

    async handleUpdateTask(e) {
        e.preventDefault();

        const taskId = document.getElementById('edit-task-id').value;
        const formData = new URLSearchParams({
            'title': document.getElementById('edit-task-title').value,
            'description': document.getElementById('edit-task-description').value,
            'quadrant': document.getElementById('edit-task-quadrant').value,
            'priority': document.getElementById('edit-task-priority').value,
            'estimated_pomodoros': document.getElementById('edit-task-pomodoros').value
        });

        try {
            const response = await fetch(`/tasks/task/${taskId}/update/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.updateTaskInDOM(taskId);
                this.closeModal();
                this.showNotification('Задача обновлена успешно!', 'success');
            } else {
                this.showNotification('Ошибка обновления задачи', 'error');
            }
        } catch (error) {
            console.error('Ошибка обновления задачи:', error);
            this.showNotification('Ошибка обновления задачи', 'error');
        }
    }

    updateTaskInDOM(taskId) {
        // В реальном приложении нужно обновить данные в DOM
        // Для простоты перезагружаем страницу
        location.reload();
    }

    async handleDeleteTask(taskId) {
        if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
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
                document.querySelector(`[data-task-id="${taskId}"]`).remove();
                this.checkEmptyQuadrants();
                this.showNotification('Задача удалена', 'success');
            } else {
                throw new Error('Ошибка удаления задачи');
            }
        } catch (error) {
            console.error('Ошибка удаления задачи:', error);
            this.showNotification('Ошибка удаления задачи', 'error');
        }
    }

    async handleCompleteTask(taskId) {
        try {
            const response = await fetch(`/tasks/task/${taskId}/complete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                document.querySelector(`[data-task-id="${taskId}"]`).remove();
                this.checkEmptyQuadrants();
                this.showNotification('Задача выполнена! 🎉', 'success');
            } else {
                throw new Error('Ошибка выполнения задачи');
            }
        } catch (error) {
            console.error('Ошибка выполнения задачи:', error);
            this.showNotification('Ошибка выполнения задачи', 'error');
        }
    }

    checkEmptyQuadrants() {
        document.querySelectorAll('.tasks-container').forEach(container => {
            if (container.children.length === 0 ||
                (container.children.length === 1 && container.querySelector('.empty-state'))) {
                this.showEmptyState(container);
            }
        });
    }

    showEmptyState(container) {
        if (!container.querySelector('.empty-state')) {
            const emptyState = document.createElement('div');
            emptyState.className = 'empty-state';
            emptyState.innerHTML = '<p>Перетащите сюда задачи или создайте новые</p>';
            container.appendChild(emptyState);
        }
    }

    openModal() {
        document.getElementById('edit-task-modal').style.display = 'block';
    }

    closeModal() {
        document.getElementById('edit-task-modal').style.display = 'none';
    }

    showFormErrors(form, errors) {
        // Очищаем предыдущие ошибки
        form.querySelectorAll('.error-message').forEach(el => el.remove());
        form.querySelectorAll('.form-control').forEach(el => el.classList.remove('error'));

        // Показываем новые ошибки
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('error');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.cssText = 'color: #dc3545; font-size: 0.8rem; margin-top: 0.25rem;';
                errorDiv.textContent = errors[fieldName][0];
                field.parentNode.appendChild(errorDiv);
            }
        });
    }

    showNotification(message, type = 'info') {
        // Используем ту же функцию уведомлений, что и в dragdrop.js
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#4ECDC4' : type === 'error' ? '#FF6B6B' : '#667eea'};
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
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    new TaskManager();
});