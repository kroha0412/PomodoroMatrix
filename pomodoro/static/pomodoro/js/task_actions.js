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

    // Инициализируем данные задачи из глобальной переменной
    if (window.taskData) {
        taskData = window.taskData;
        console.log('Task data loaded from window:', taskData);
    }

    // Инициализируем настройки из глобальной переменной
    if (window.settingsData) {
        settingsData = window.settingsData;
        console.log('Settings data loaded from window:', settingsData);
    }

    // Назначаем обработчики событий
    initEventListeners();

    // Инициализация прогресса при загрузке
    updateTaskProgressDisplay();

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
            // Обновляем данные задачи
            if (taskData) {
                taskData.estimated_pomodoros = estimatedPomodoros;
            }

            // Обновляем отображение прогресса
            updateTaskProgressDisplay();

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

// Функция завершения задачи - ИСПРАВЛЕННАЯ ВЕРСИЯ
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

        // Используем AJAX запрос вместо скрытой формы
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
            console.log('Response data:', data);

            if (data.success) {
                // Показываем уведомление об успехе
                showNotification(data.message || 'Задача успешно завершена!', 'success');

                // Ждем 1.5 секунды, чтобы пользователь увидел сообщение, затем редирект
                setTimeout(() => {
                    // Используем redirect_url из ответа или стандартный URL
                    const redirectUrl = data.redirect_url || '/tasks/matrix/';
                    console.log('Redirecting to:', redirectUrl);
                    window.location.href = redirectUrl;
                }, 1500);
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

// Функция обновления отображения прогресса задачи
function updateTaskProgressDisplay() {
    const completed = taskData?.completed_pomodoros || 0;
    const estimated = taskData?.estimated_pomodoros || 1;

    console.log('Updating progress display:', completed + '/' + estimated);

    // Обновляем текстовый счетчик
    const progressTextElement = document.getElementById('progress-text');
    if (progressTextElement) {
        progressTextElement.innerHTML =
            `Выполнено <span class="completed">${completed}</span> из ` +
            `<span class="total">${estimated}</span> Pomodoro`;
    }

    // Обновляем прогресс-бар
    const progressBar = document.getElementById('task-progress-bar');
    if (progressBar) {
        const percentage = estimated > 0 ? (completed / estimated) * 100 : 0;
        progressBar.style.width = `${Math.min(percentage, 100)}%`;
        console.log('Progress bar updated to:', percentage.toFixed(1) + '%');
    }

    // Обновляем поле ввода оценки
    const estimationInput = document.getElementById('estimated-pomodoros');
    if (estimationInput && taskData) {
        estimationInput.value = taskData.estimated_pomodoros;
    }
}

// Экспорт функций для использования в других файлах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCSRFToken,
        showNotification,
        updateEstimation,
        completeTask,
        updateTaskProgressDisplay,
        setTaskData: function(data) { taskData = data; },
        setSettingsData: function(data) { settingsData = data; },
        setCsrfToken: function(token) { csrfToken = token; }
    };
}