// pomodoro/static/pomodoro/js/timer.js
class PomodoroTimer {
    constructor() {
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
        this.loadTodayCount();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Обновление настроек
        document.getElementById('timer-settings-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        document.getElementById('timer-display').textContent = display;
        document.getElementById('timer-phase').textContent = this.getPhaseText();
        document.getElementById('cycle-count').textContent = this.completedCycles + 1;
        document.getElementById('total-cycles').textContent = this.cyclesBeforeLongBreak;

        // Обновляем прогресс-бар
        const totalTime = this.getCurrentPhaseDuration();
        const progress = ((totalTime - this.timeLeft) / totalTime) * 100;
        document.getElementById('phase-progress').style.width = `${progress}%`;

        // Обновляем цвета в зависимости от фазы
        this.updateTimerColors();
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
        const timerCard = document.querySelector('.timer-card');
        const timerTime = document.getElementById('timer-display');

        timerCard.classList.remove('work-mode', 'break-mode', 'long-break-mode');
        timerTime.classList.remove('work-color', 'break-color', 'long-break-color');

        switch(this.currentPhase) {
            case 'work':
                timerCard.classList.add('work-mode');
                timerTime.classList.add('work-color');
                break;
            case 'short_break':
                timerCard.classList.add('break-mode');
                timerTime.classList.add('break-color');
                break;
            case 'long_break':
                timerCard.classList.add('long-break-mode');
                timerTime.classList.add('long-break-color');
                break;
        }
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

        // Автозапуск следующей фазы (опционально)
        // setTimeout(() => this.startTimer(), 1000);
    }

    updateButtonStates() {
        const startBtn = document.getElementById('start-timer');
        const pauseBtn = document.getElementById('pause-timer');
        const skipBtn = document.getElementById('skip-timer');

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

    async startSession() {
        try {
            const response = await fetch('/pomodoro/api/start_session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    task_id: taskData.id,
                    session_type: this.currentPhase
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentSessionId = data.session_id;
                this.showNotification(data.message);
                this.updateTodayCount(1);
            }
        } catch (error) {
            console.error('Error starting session:', error);
        }
    }

    async endSession(status = 'completed') {
        try {
            if (!this.currentSessionId) return;

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

    async saveSettings() {
        try {
            const formData = new FormData(document.getElementById('timer-settings-form'));

            const response = await fetch('/users/profile/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.showNotification('Настройки сохранены!');

                // Обновляем таймер с новыми настройками
                this.workDuration = parseInt(document.getElementById('pomodoro-duration').value) * 60;
                this.shortBreak = parseInt(document.getElementById('short-break-duration').value) * 60;
                this.longBreak = parseInt(document.getElementById('long-break-duration').value) * 60;
                this.cyclesBeforeLongBreak = parseInt(document.getElementById('pomodoros-before-long-break').value);

                this.timeLeft = this.workDuration;
                this.updateDisplay();
            }
        } catch (error) {
            console.error('Error saving settings:', error);
        }
    }

    updateTaskProgress(progress) {
        // Обновляем прогресс-бар задачи
        const percentage = (progress.completed / progress.total) * 100;
        document.querySelector('.progress-fill').style.width = `${percentage}%`;
        document.querySelector('.progress-text').textContent =
            `${progress.completed} из ${progress.total} Pomodoro`;
    }

    updateTodayCount(increment = 0) {
        const countElement = document.getElementById('today-count');
        let count = parseInt(countElement.textContent);

        if (increment > 0) {
            count += increment;
            countElement.textContent = count;
        }
    }

    loadTodayCount() {
        // Можно загружать через API если нужно
    }

    showNotification(message) {
        const notification = document.getElementById('notification');
        const messageElement = document.getElementById('notification-message');

        messageElement.textContent = message;
        notification.classList.remove('hidden');

        // Автоматически скрыть через 3 секунды
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 3000);
    }
}

// Глобальные функции для кнопок
let pomodoroTimer;

function startTimer() {
    if (!pomodoroTimer) {
        pomodoroTimer = new PomodoroTimer();
    }
    pomodoroTimer.startTimer();
}

function pauseTimer() {
    if (pomodoroTimer) {
        pomodoroTimer.pauseTimer();
    }
}

function stopTimer() {
    if (pomodoroTimer) {
        pomodoroTimer.stopTimer();
    }
}

function skipPhase() {
    if (pomodoroTimer) {
        pomodoroTimer.skipPhase();
    }
}

function completeTask() {
    if (confirm('Завершить эту задачу?')) {
        // Реализация завершения задачи
        window.location.href = `/tasks/task/${taskData.id}/complete/`;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    pomodoroTimer = new PomodoroTimer();

    // Добавляем звуковые уведомления (опционально)
    try {
        window.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
        console.log('Web Audio API не поддерживается');
    }
});