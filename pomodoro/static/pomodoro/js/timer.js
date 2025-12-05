// pomodoro/static/pomodoro/js/timer.js
// Основной файл для работы Pomodoro таймера

class PomodoroTimer {
    constructor() {
        // Проверяем что данные загружены
        if (!settingsData) {
            console.error('Settings data not loaded!');
            return;
        }

        this.workDuration = parseInt(settingsData.workDuration) * 60; // в секунды
        this.shortBreak = parseInt(settingsData.shortBreak) * 60;
        this.longBreak = parseInt(settingsData.longBreak) * 60;
        this.cyclesBeforeLongBreak = parseInt(settingsData.cyclesBeforeLongBreak);

        this.timeLeft = this.workDuration;
        this.currentPhase = 'work'; // 'work', 'short_break', 'long_break'
        this.isRunning = false;
        this.timerInterval = null;
        this.completedCycles = 0;
        this.currentSessionId = null;

        this.init();
    }

    init() {
        this.updateDisplay();
        this.setupEventListeners();
        console.log('PomodoroTimer initialized');
    }

    setupEventListeners() {
        // Обработчики для кнопок таймера
        const startBtn = document.getElementById('start-timer');
        const pauseBtn = document.getElementById('pause-timer');
        const stopBtn = document.getElementById('stop-timer');
        const skipBtn = document.getElementById('skip-timer');

        if (startBtn) {
            startBtn.addEventListener('click', () => this.startTimer());
        }

        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.pauseTimer());
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopTimer());
        }

        if (skipBtn) {
            skipBtn.addEventListener('click', () => this.skipPhase());
        }
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        const timerDisplay = document.getElementById('timer-display');
        const timerPhase = document.getElementById('timer-phase');
        const cycleCounter = document.getElementById('cycle-counter');

        if (timerDisplay) {
            timerDisplay.textContent = display;
        }

        if (timerPhase) {
            timerPhase.textContent = this.getPhaseText();
        }

        // Обновляем счетчик циклов
        if (cycleCounter) {
            cycleCounter.textContent = `${this.completedCycles + 1}/${this.cyclesBeforeLongBreak}`;
        }

        // Обновляем прогресс кругового индикатора
        const totalTime = this.getCurrentPhaseDuration();
        const progress = ((totalTime - this.timeLeft) / totalTime) * 100;

        const timerCircle = document.getElementById('timer-circle');
        if (timerCircle) {
            timerCircle.style.setProperty('--progress', progress);
        }

        // Обновляем точки циклов
        for (let i = 1; i <= this.cyclesBeforeLongBreak; i++) {
            const cycleDot = document.getElementById(`cycle-dot-${i}`);
            if (cycleDot) {
                cycleDot.classList.remove('active');
                if (i <= this.completedCycles + 1) {
                    cycleDot.classList.add('active');
                }
            }
        }

        // Обновляем цвета в зависимости от фазы
        this.updateTimerColors();

        // Обновляем состояние кнопок
        this.updateButtonStates();
    }

    getPhaseText() {
        switch(this.currentPhase) {
            case 'work': return 'Работа';
            case 'short_break': return 'Короткий перерыв';
            case 'long_break': return 'Длинный перерыв';
            default: return 'Готов к работе';
        }
    }

    updateTimerColors() {
        const timerCircle = document.getElementById('timer-circle');
        if (!timerCircle) return;

        // Убираем все классы цветов
        timerCircle.classList.remove('work-mode', 'break-mode', 'long-break-mode');

        let gradientColor;
        switch(this.currentPhase) {
            case 'work':
                timerCircle.classList.add('work-mode');
                gradientColor = '#4ECDC4';
                break;
            case 'short_break':
                timerCircle.classList.add('break-mode');
                gradientColor = '#FFC107';
                break;
            case 'long_break':
                timerCircle.classList.add('long-break-mode');
                gradientColor = '#17a2b8';
                break;
            default:
                gradientColor = '#4ECDC4';
        }

        const progress = this.getProgressPercentage();
        timerCircle.style.background = `conic-gradient(
            ${gradientColor} 0deg,
            ${gradientColor} calc(${progress} * 3.6deg),
            #f0f0f0 calc(${progress} * 3.6deg),
            #f0f0f0 360deg
        )`;
    }

    getProgressPercentage() {
        const totalTime = this.getCurrentPhaseDuration();
        return ((totalTime - this.timeLeft) / totalTime) * 100;
    }

    getCurrentPhaseDuration() {
        switch(this.currentPhase) {
            case 'work': return this.workDuration;
            case 'short_break': return this.shortBreak;
            case 'long_break': return this.longBreak;
            default: return this.workDuration;
        }
    }

    async startTimer() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.updateButtonStates();

        // Если таймер только запускается, а не возобновляется
        if (this.timeLeft === this.getCurrentPhaseDuration()) {
            await this.startSession();
        }

        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();

            if (this.timeLeft <= 0) {
                clearInterval(this.timerInterval);
                this.completePhase();
            }
        }, 1000);
    }

    pauseTimer() {
        if (!this.isRunning) return;

        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.updateButtonStates();
    }

    stopTimer() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.timeLeft = this.getCurrentPhaseDuration();
        this.updateDisplay();
        this.updateButtonStates();

        if (this.currentSessionId) {
            this.endSession('cancelled');
        }
    }

    skipPhase() {
        clearInterval(this.timerInterval);
        this.completePhase();
    }

    async completePhase() {
        this.isRunning = false;

        // Завершаем текущую сессию
        if (this.currentSessionId) {
            await this.endSession('completed');
        }

        // Определяем следующую фазу
        if (this.currentPhase === 'work') {
            this.completedCycles++;

            // Проверяем, нужен ли длинный перерыв
            if (this.completedCycles >= this.cyclesBeforeLongBreak) {
                this.currentPhase = 'long_break';
                this.completedCycles = 0;
                this.showNotification('Отличная работа! Время для длинного перерыва!');
            } else {
                this.currentPhase = 'short_break';
                this.showNotification('Хорошая работа! Время для короткого перерыва!');
            }
        } else {
            this.currentPhase = 'work';
            this.showNotification('Перерыв закончился! Готовы к работе?');
        }

        // Обновляем таймер
        this.timeLeft = this.getCurrentPhaseDuration();
        this.updateDisplay();
        this.updateButtonStates();
    }

    updateButtonStates() {
        const startBtn = document.getElementById('start-timer');
        const pauseBtn = document.getElementById('pause-timer');
        const skipBtn = document.getElementById('skip-timer');

        if (startBtn && pauseBtn && skipBtn) {
            if (this.isRunning) {
                startBtn.disabled = true;
                pauseBtn.disabled = false;
                skipBtn.disabled = false;
            } else {
                startBtn.disabled = false;
                pauseBtn.disabled = true;
                skipBtn.disabled = this.timeLeft === this.getCurrentPhaseDuration();
            }
        }
    }

    async startSession() {
        try {
            // Получаем CSRF токен
            const csrfToken = getCSRFToken();
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }

            // Получаем ID задачи
            let taskId = null;
            if (taskData && taskData.id) {
                taskId = taskData.id;
            }

            if (!taskId) {
                throw new Error('Task ID not found');
            }

            const response = await fetch('/pomodoro/api/start_session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    task_id: taskId,
                    session_type: this.currentPhase
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentSessionId = data.session_id;
                this.showNotification(data.message);
            }
        } catch (error) {
            console.error('Error starting session:', error);
            this.showNotification('Ошибка запуска сессии', 'error');
        }
    }

    async endSession(status = 'completed') {
        try {
            if (!this.currentSessionId) return;

            const csrfToken = getCSRFToken();
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }

            const response = await fetch('/pomodoro/api/end_session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    status: status
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentSessionId = null;
                this.showNotification(data.message);

                // Обновляем прогресс задачи
                if (data.task_progress) {
                    this.updateTaskProgress(data.task_progress);
                }
            }
        } catch (error) {
            console.error('Error ending session:', error);
        }
    }

    updateTaskProgress(progress) {
        // Обновляем прогресс-бар задачи
        const progressBar = document.getElementById('task-progress-bar');
        if (progressBar) {
            const percentage = (progress.completed / progress.total) * 100;
            progressBar.style.width = `${percentage}%`;
        }

        // Обновляем текст прогресса
        const progressText = document.getElementById('progress-text');
        if (progressText) {
            progressText.innerHTML =
                `Выполнено <span class="completed">${progress.completed}</span> из
                 <span class="total">${progress.total}</span> Pomodoro выполнено`;
        }
    }

    showNotification(message, type = 'success') {
        // Используем функцию из task_actions.js если она доступна
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        } else {
            // Создаем простейшее уведомление
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Глобальная функция для получения CSRF токена
function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Timer module loaded');

    // Инициализируем таймер только если есть необходимые данные
    if (typeof settingsData !== 'undefined') {
        try {
            window.pomodoroTimer = new PomodoroTimer();
            console.log('Pomodoro timer initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Pomodoro timer:', error);
        }
    } else {
        console.warn('Settings data not available, timer not initialized');
    }
});