// pomodoro/static/pomodoro/js/timer.js - ИСПРАВЛЕННАЯ ВЕРСИЯ
console.log('Timer script loading...');

class PomodoroTimer {
    constructor() {
        console.log('Creating PomodoroTimer instance...');

        // Получаем настройки из глобальной переменной или используем значения по умолчанию
        const settings = window.settingsData || {};

        this.workDuration = (parseInt(settings.workDuration) || 25) * 60;  // в секундах
        this.shortBreak = (parseInt(settings.shortBreak) || 5) * 60;
        this.longBreak = (parseInt(settings.longBreak) || 15) * 60;
        this.cyclesBeforeLongBreak = parseInt(settings.cyclesBeforeLongBreak) || 4;

        console.log('Timer settings:', {
            workDuration: this.workDuration / 60 + ' мин',
            shortBreak: this.shortBreak / 60 + ' мин',
            longBreak: this.longBreak / 60 + ' мин',
            cyclesBeforeLongBreak: this.cyclesBeforeLongBreak
        });

        this.timeLeft = this.workDuration;
        this.currentPhase = 'work';
        this.isRunning = false;
        this.timerInterval = null;
        this.completedCycles = 0;

        this.init();
    }

    init() {
        console.log('Initializing timer...');
        this.updateDisplay();
        this.setupEventListeners();
        console.log('Timer initialized successfully!');
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');

        // Основные кнопки управления
        const startBtn = document.getElementById('start-timer');
        const pauseBtn = document.getElementById('pause-timer');
        const stopBtn = document.getElementById('stop-timer');
        const skipBtn = document.getElementById('skip-timer');

        // Проверяем наличие кнопок
        if (!startBtn) {
            console.error('❌ Кнопка "start-timer" не найдена!');
            return;
        }
        if (!pauseBtn) console.warn('⚠️ Кнопка "pause-timer" не найдена');
        if (!stopBtn) console.warn('⚠️ Кнопка "stop-timer" не найдена');
        if (!skipBtn) console.warn('⚠️ Кнопка "skip-timer" не найдена');

        // Вешаем обработчики
        startBtn.addEventListener('click', (e) => {
            console.log('🎯 Кнопка "Старт" нажата');
            e.preventDefault();
            e.stopPropagation();
            this.startTimer();
        });

        if (pauseBtn) {
            pauseBtn.addEventListener('click', (e) => {
                console.log('⏸️ Кнопка "Пауза" нажата');
                e.preventDefault();
                this.pauseTimer();
            });
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', (e) => {
                console.log('⏹️ Кнопка "Стоп" нажата');
                e.preventDefault();
                this.stopTimer();
            });
        }

        if (skipBtn) {
            skipBtn.addEventListener('click', (e) => {
                console.log('⏭️ Кнопка "Пропустить" нажата');
                e.preventDefault();
                this.skipPhase();
            });
        }
    }

    updateDisplay() {
        // Форматируем время (MM:SS)
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        // Обновляем отображение времени
        const timerDisplay = document.getElementById('timer-display');
        if (timerDisplay) {
            timerDisplay.textContent = timeString;
        }

        // Обновляем текст фазы
        const timerPhase = document.getElementById('timer-phase');
        if (timerPhase) {
            timerPhase.textContent = this.getPhaseText();
        }

        // Обновляем круговой прогресс
        this.updateProgressCircle();

        // Обновляем состояние кнопок
        this.updateButtonStates();
    }

    getPhaseText() {
        const phases = {
            'work': 'Работа',
            'short_break': 'Короткий перерыв',
            'long_break': 'Длинный перерыв'
        };
        return phases[this.currentPhase] || 'Готов к работе';
    }

    updateProgressCircle() {
        const circle = document.getElementById('timer-circle');
        if (!circle) return;

        const totalTime = this.getCurrentPhaseDuration();
        const progress = ((totalTime - this.timeLeft) / totalTime) * 100;

        // Цвета для разных фаз
        const colors = {
            'work': '#4ECDC4',
            'short_break': '#FFC107',
            'long_break': '#17a2b8'
        };

        const color = colors[this.currentPhase] || '#4ECDC4';

        // Создаем градиент для кругового индикатора
        circle.style.background = `conic-gradient(
            ${color} 0deg,
            ${color} ${progress * 3.6}deg,
            #f0f0f0 ${progress * 3.6}deg,
            #f0f0f0 360deg
        )`;
    }

    getCurrentPhaseDuration() {
        const durations = {
            'work': this.workDuration,
            'short_break': this.shortBreak,
            'long_break': this.longBreak
        };
        return durations[this.currentPhase] || this.workDuration;
    }

    startTimer() {
        if (this.isRunning) {
            console.log('⚠️ Таймер уже запущен');
            return;
        }

        console.log('🚀 Запуск таймера...');
        this.isRunning = true;

        // Если таймер на нуле, сбрасываем его
        if (this.timeLeft <= 0) {
            this.timeLeft = this.getCurrentPhaseDuration();
        }

        this.updateButtonStates();

        // Запускаем интервал
        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();

            if (this.timeLeft <= 0) {
                console.log('⏰ Таймер завершен!');
                clearInterval(this.timerInterval);
                this.completePhase();
            }
        }, 1000);

        this.showNotification('Таймер запущен!', 'success');
    }

    pauseTimer() {
        if (!this.isRunning) return;

        console.log('⏸️ Пауза таймера');
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.updateButtonStates();
        this.showNotification('Таймер на паузе', 'warning');
    }

    stopTimer() {
        console.log('⏹️ Остановка таймера');
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.timeLeft = this.getCurrentPhaseDuration();
        this.updateDisplay();
        this.updateButtonStates();
        this.showNotification('Таймер остановлен', 'info');
    }

    skipPhase() {
        console.log('⏭️ Пропуск фазы');
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.completePhase();
    }

    completePhase() {
        console.log('✅ Завершение фазы:', this.currentPhase);

        // Если завершилась рабочая фаза - увеличиваем счетчик Pomodoro
        if (this.currentPhase === 'work') {
            this.incrementCompletedPomodoros();
            this.completedCycles++;

            if (this.completedCycles >= this.cyclesBeforeLongBreak) {
                this.currentPhase = 'long_break';
                this.completedCycles = 0;
                this.showNotification('Отличная работа! Время для длинного перерыва 🎉', 'success');
            } else {
                this.currentPhase = 'short_break';
                this.showNotification('Хорошая работа! Короткий перерыв ☕', 'success');
            }
        } else {
            this.currentPhase = 'work';
            this.showNotification('Перерыв закончился! Готовы к работе? 💪', 'info');
        }

        this.timeLeft = this.getCurrentPhaseDuration();
        this.updateDisplay();
        this.updateButtonStates();

        // Проигрываем звук (если браузер поддерживает)
        this.playNotificationSound();
    }

    // НОВЫЙ МЕТОД: увеличение счетчика выполненных Pomodoro
    incrementCompletedPomodoros() {
        if (!window.taskData) {
            console.warn('Нет данных о задаче');
            return;
        }

        // Увеличиваем счетчик в данных задачи
        window.taskData.completed_pomodoros = (window.taskData.completed_pomodoros || 0) + 1;

        console.log('🍅 Увеличиваем счетчик Pomodoro:', window.taskData.completed_pomodoros);

        // Обновляем отображение на странице
        this.updateTaskProgress();

        // Отправляем данные на сервер (опционально)
        this.sendProgressToServer();
    }

    // НОВЫЙ МЕТОД: обновление отображения прогресса
    updateTaskProgress() {
        const completed = window.taskData?.completed_pomodoros || 0;
        const estimated = window.taskData?.estimated_pomodoros || 1;

        // Обновляем текстовый счетчик в блоке с id="progress-text"
        const progressTextElement = document.getElementById('progress-text');
        if (progressTextElement) {
            progressTextElement.innerHTML =
                `Выполнено <span class="completed">${completed}</span> из ` +
                `<span class="total">${estimated}</span> Pomodoro`;
            console.log('📝 Текст прогресса обновлен:', completed + '/' + estimated);
        }

        // Обновляем прогресс-бар
        const progressBar = document.getElementById('task-progress-bar');
        if (progressBar) {
            const percentage = estimated > 0 ? (completed / estimated) * 100 : 0;
            progressBar.style.width = `${Math.min(percentage, 100)}%`;
            console.log('📊 Прогресс обновлен:', percentage.toFixed(1) + '%');
        }

        // НЕ обновляем прогресс в шапке - она удалена
    }

    // НОВЫЙ МЕТОД: отправка прогресса на сервер
    async sendProgressToServer() {
        try {
            const csrfToken = window.getCSRFToken();
            if (!csrfToken) {
                console.warn('CSRF токен не найден');
                return;
            }

            const taskId = window.taskData?.id;
            if (!taskId) {
                console.warn('ID задачи не найден');
                return;
            }

            const formData = new FormData();
            formData.append('completed_pomodoros', window.taskData.completed_pomodoros);
            formData.append('csrfmiddlewaretoken', csrfToken);

            const response = await fetch(`/pomodoro/task/${taskId}/update_progress/`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    console.log('✅ Прогресс сохранен на сервере');
                }
            }
        } catch (error) {
            console.error('❌ Ошибка сохранения прогресса:', error);
        }
    }

    updateButtonStates() {
        const startBtn = document.getElementById('start-timer');
        const pauseBtn = document.getElementById('pause-timer');
        const skipBtn = document.getElementById('skip-timer');

        if (startBtn) {
            startBtn.disabled = this.isRunning;
            startBtn.innerHTML = this.isRunning
                ? '<span class="btn-icon">▶</span><span class="btn-text">Запущено</span>'
                : '<span class="btn-icon">▶</span><span class="btn-text">Начать Pomodoro</span>';
        }

        if (pauseBtn) {
            pauseBtn.disabled = !this.isRunning;
        }

        if (skipBtn) {
            skipBtn.disabled = !this.isRunning && this.timeLeft === this.getCurrentPhaseDuration();
        }
    }

    showNotification(message, type = 'info') {
        console.log(`📢 Уведомление (${type}):`, message);

        // Показываем уведомление на странице если есть элемент
        const notificationEl = document.getElementById('notification');
        const messageEl = document.getElementById('notification-message');

        if (notificationEl && messageEl) {
            messageEl.textContent = message;

            // Цвета для разных типов уведомлений
            const colors = {
                'success': '#4ECDC4',
                'error': '#dc3545',
                'warning': '#FFC107',
                'info': '#17a2b8'
            };

            notificationEl.style.background = colors[type] || '#4ECDC4';
            notificationEl.classList.remove('hidden');

            // Автоматически скрываем через 3 секунды
            setTimeout(() => {
                notificationEl.classList.add('hidden');
            }, 3000);
        }

        // Также можно использовать браузерные уведомления
        if (Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', { body: message });
        }
    }

    playNotificationSound() {
        // Создаем простой звуковой сигнал
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = 800;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            console.log('Браузер не поддерживает Web Audio API');
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM загружен, инициализируем таймер...');

    // Небольшая задержка для гарантии загрузки всех элементов
    setTimeout(() => {
        try {
            console.log('⚙️ Создаем экземпляр PomodoroTimer...');
            window.pomodoroTimer = new PomodoroTimer();
            console.log('✅ PomodoroTimer успешно создан!');

        } catch (error) {
            console.error('❌ Ошибка при создании PomodoroTimer:', error);
        }
    }, 100);
});

// Экспортируем для тестирования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PomodoroTimer;
}