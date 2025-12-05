// pomodoro/static/pomodoro/js/task_actions.js
// Функции для работы с задачами на странице Pomodoro

// Глобальные переменные
let taskData = null;
let settingsData = null;
let csrfToken = '';

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Получаем CSRF токен
    csrfToken = getCSRFToken();

    // Назначаем обработчики событий
    initEventListeners();

    // Отладочная информация
    console.log('Task actions initialized');
    console.log('CSRF Token present:', csrfToken ? 'Yes' : 'No');
});

// Получение CSRF токена
function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }

    // Альтернативный способ поиска токена
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }

    console.error('CSRF token not found!');
    return '';
}

// Инициализация обработчиков событий
function initEventListeners() {
    // Кнопка сохранения оценки
    const saveBtn = document.getElementById('save-estimation-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', updateEstimation);
    }

    // Кнопка завершения задачи
    const completeBtn = document.getElementById('complete-task-btn');
    if (completeBtn) {
        completeBtn.addEventListener('click', completeTask);
    }

    // Поле ввода оценки - сохранение по Enter
    const estimatedInput = document.getElementById('estimated-pomodoros');
    if (estimatedInput) {
        estimatedInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                updateEstimation();
            }
        });
    }
}

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const messageElement = document.getElementById('notification-message');

    if (notification && messageElement) {
        messageElement.textContent = message;

        // Устанавливаем цвет в зависимости от типа
        if (type === 'error') {
            notification.style.background = '#dc3545';
        } else if (type === 'warning') {
            notification.style.background = '#FFC107';
            notification.style.color = '#333';
        } else {
            notification.style.background = '#4ECDC4';
            notification.style.color = 'white';
        }

        notification.classList.remove('hidden');

        // Автоматически скрыть через 3 секунды
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 3000);
    }
}

// Функция обновления оценки Pomodoro
function updateEstimation() {
    const estimatedInput = document.getElementById('estimated-pomodoros');
    if (!estimatedInput) {
        showNotification('Поле оценки не найдено', 'error');
        return;
    }

    const estimatedPomodoros = parseInt(estimatedInput.value);

    // Валидация
    if (!estimatedPomodoros || estimatedPomodoros < 1 || estimatedPomodoros > 20) {
        showNotification('Введите число от 1 до 20', 'error');
        return;
    }

    const saveBtn = document.getElementById('save-estimation-btn');
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'Сохранение...';
    saveBtn.disabled = true;

    // Создаем FormData для отправки
    const formData = new FormData();
    formData.append('title', taskData ? taskData.title : document.querySelector('.task-title').textContent);
    formData.append('description', '');
    formData.append('estimated_pomodoros', estimatedPomodoros);
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Получаем ID задачи из URL или данных
    let taskId = null;
    if (taskData && taskData.id) {
        taskId = taskData.id;
    } else {
        // Пытаемся извлечь ID из URL
        const urlParts = window.location.pathname.split('/');
        const taskIndex = urlParts.indexOf('task') + 1;
        if (taskIndex < urlParts.length && !isNaN(urlParts[taskIndex])) {
            taskId = parseInt(urlParts[taskIndex]);
        }
    }

    if (!taskId) {
        showNotification('Не удалось определить ID задачи', 'error');
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
        return;
    }

    console.log(`Updating task ${taskId} with ${estimatedPomodoros} pomodoros`);

    fetch(`/tasks/task/${taskId}/update/`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Обновляем данные на странице
            if (taskData) {
                taskData.totalPomodoros = estimatedPomodoros;
            }

            // Обновляем прогресс-бар
            const progressBar = document.getElementById('task-progress-bar');
            const progressText = document.getElementById('progress-text');
            const completedElement = document.querySelector('.progress-text .completed');
            const totalElement = document.querySelector('.progress-text .total');

            if (progressBar && progressText) {
                // Пересчитываем процент выполнения
                let completed = 0;
                if (completedElement) {
                    completed = parseInt(completedElement.textContent) || 0;
                }

                let percentage = 0;
                if (estimatedPomodoros > 0) {
                    percentage = (completed / estimatedPomodoros) * 100;
                }

                progressBar.style.width = `${percentage}%`;

                // Обновляем текст прогресса
                if (completedElement && totalElement) {
                    completedElement.textContent = completed;
                    totalElement.textContent = estimatedPomodoros;
                } else {
                    progressText.innerHTML =
                        `Выполнено <span class="completed">${completed}</span> из
                         <span class="total">${estimatedPomodoros}</span> Pomodoro`;
                }
            }

            // Обновляем заголовок прогресса
            const progressSummary = document.querySelector('.task-progress-summary .total');
            if (progressSummary) {
                progressSummary.textContent = estimatedPomodoros;
            }

            showNotification('Оценка успешно обновлена!');
        } else {
            showNotification('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка соединения: ' + error.message, 'error');
    })
    .finally(() => {
        // Восстанавливаем кнопку
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    });
}

// Функция завершения задачи
function completeTask() {
    // Получаем название задачи
    const taskTitle = taskData ? taskData.title : document.querySelector('.task-title').textContent;

    if (confirm(`Завершить задачу "${taskTitle}"?`)) {
        const completeBtn = document.getElementById('complete-task-btn');
        const originalText = completeBtn.innerHTML;
        completeBtn.innerHTML = 'Завершение...';
        completeBtn.disabled = true;

        // Получаем ID задачи
        let taskId = null;
        if (taskData && taskData.id) {
            taskId = taskData.id;
        } else {
            // Пытаемся извлечь ID из URL
            const urlParts = window.location.pathname.split('/');
            const taskIndex = urlParts.indexOf('task') + 1;
            if (taskIndex < urlParts.length && !isNaN(urlParts[taskIndex])) {
                taskId = parseInt(urlParts[taskIndex]);
            }
        }

        if (!taskId) {
            showNotification('Не удалось определить ID задачи', 'error');
            completeBtn.innerHTML = originalText;
            completeBtn.disabled = false;
            return;
        }

        console.log(`Completing task ${taskId}`);

        // Используем скрытую форму для гарантированной отправки
        const form = document.getElementById('complete-task-form');
        if (form) {
            form.submit();
        } else {
            // Альтернативный способ через AJAX
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrfToken);

            fetch(`/pomodoro/task/${taskId}/complete/`, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Редирект на матрицу
                    window.location.href = data.redirect_url || '/tasks/matrix/';
                } else {
                    showNotification('Ошибка: ' + (data.error || 'Неизвестная ошибка'), 'error');
                    completeBtn.innerHTML = originalText;
                    completeBtn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Ошибка соединения: ' + error.message, 'error');
                completeBtn.innerHTML = originalText;
                completeBtn.disabled = false;
            });
        }
    }
}

// Экспорт функций для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCSRFToken,
        showNotification,
        updateEstimation,
        completeTask,
        setTaskData: function(data) { taskData = data; },
        setSettingsData: function(data) { settingsData = data; },
        setCsrfToken: function(token) { csrfToken = token; }
    };
}