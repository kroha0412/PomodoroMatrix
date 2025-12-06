// analytics/static/analytics/js/analytics.js
/**
 * Основной скрипт для модуля аналитики.
 * Обеспечивает интерактивность, переключение вкладок и работу с графиками.
 */

// Глобальные переменные для хранения экземпляров графиков
let productivityChart = null;
let quadrantChart = null;

function waitForChartData(callback) {
    // Ждем пока данные будут доступны
    if (typeof window.chartData !== 'undefined') {
        callback();
    } else {
        setTimeout(function() {
            waitForChartData(callback);
        }, 100);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics module loaded');

    // Ждем данных, потом инициализируем
    waitForChartData(function() {
        console.log('Chart data ready, initializing components...');

        // Инициализация всех компонентов
        initNavigation();
        initCharts();
        initFilters();
    });
});

// ============ ИНИЦИАЛИЗАЦИЯ НАВИГАЦИИ ============
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Убираем активный класс у всех кнопок
            navButtons.forEach(btn => btn.classList.remove('active'));

            // Добавляем активный класс текущей кнопке
            this.classList.add('active');

            // Скрываем все вкладки
            tabContents.forEach(tab => tab.classList.remove('active'));

            // Показываем нужную вкладку
            const tabId = this.dataset.tab + '-tab';
            const targetTab = document.getElementById(tabId);
            if (targetTab) {
                targetTab.classList.add('active');

                // Перерисовываем графики при переключении вкладок
                setTimeout(() => {
                    if (productivityChart) productivityChart.resize();
                    if (quadrantChart) quadrantChart.resize();
                }, 100);
            }
        });
    });
}

// ============ ИНИЦИАЛИЗАЦИЯ ГРАФИКОВ ============
function initCharts() {
    console.log('Initializing charts...');
    console.log('Window.chartData:', window.chartData);

    // Проверяем наличие Chart.js
    if (typeof Chart === 'undefined') {
        console.error('Chart.js не загружен');
        // Пробуем загрузить динамически
        loadChartJS();
        return;
    }

    // Уничтожаем старые графики, если они существуют
    if (productivityChart) {
        productivityChart.destroy();
        productivityChart = null;
    }
    if (quadrantChart) {
        quadrantChart.destroy();
        quadrantChart = null;
    }

    // Проверяем наличие данных
    if (!window.chartData) {
        console.error('Chart data not found in window object');
        return;
    }

    // Инициализируем все графики
    initProductivityChart();
    initQuadrantChart();
}

function loadChartJS() {
    console.log('Trying to load Chart.js dynamically...');
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = function() {
        console.log('Chart.js dynamically loaded');
        initCharts();
    };
    script.onerror = function() {
        console.error('Failed to load Chart.js');
    };
    document.head.appendChild(script);
}

function initProductivityChart() {
    const ctx = document.getElementById('productivityChart');
    if (!ctx) {
        console.error('Productivity chart canvas not found');
        return;
    }

    // Данные из глобальной переменной
    const chartData = window.chartData;
    if (!chartData || !chartData.daily) {
        console.error('Daily chart data not found in chartData');
        return;
    }

    // Проверяем, есть ли данные для отображения
    if (!chartData.daily.labels || chartData.daily.labels.length === 0) {
        console.warn('No labels for productivity chart');
        // Создаем тестовые данные для отладки
        createTestProductivityChart(ctx);
        return;
    }

    try {
        productivityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.daily.labels,
                datasets: [
                    {
                        label: 'Продуктивность',
                        data: chartData.daily.productivity,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Фокус',
                        data: chartData.daily.focus,
                        borderColor: '#4ECDC4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
        console.log('Productivity chart initialized with data:', {
            labels: chartData.daily.labels.length,
            productivityPoints: chartData.daily.productivity.length,
            focusPoints: chartData.daily.focus.length
        });
    } catch (error) {
        console.error('Error initializing productivity chart:', error);
        // Пробуем создать тестовый график
        createTestProductivityChart(ctx);
    }
}

function createTestProductivityChart(ctx) {
    console.log('Creating test productivity chart');
    try {
        productivityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['День 1', 'День 2', 'День 3'],
                datasets: [{
                    label: 'Тестовая продуктивность',
                    data: [50, 75, 60],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        console.log('Test productivity chart created');
    } catch (error) {
        console.error('Failed to create test chart:', error);
    }
}

function initQuadrantChart() {
    const ctx = document.getElementById('quadrantChart');
    if (!ctx) {
        console.error('Quadrant chart canvas not found');
        return;
    }

    const chartData = window.chartData;
    if (!chartData || !chartData.quadrants) {
        console.error('Quadrant chart data not found in chartData');
        return;
    }

    // Проверяем, есть ли данные для отображения
    if (!chartData.quadrants.data || chartData.quadrants.data.length === 0) {
        console.warn('No data for quadrant chart');
        // Создаем тестовые данные для отладки
        createTestQuadrantChart(ctx);
        return;
    }

    try {
        quadrantChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.quadrants.labels,
                datasets: [{
                    data: chartData.quadrants.data,
                    backgroundColor: chartData.quadrants.colors,
                    borderWidth: 1,
                    borderColor: 'rgba(255, 255, 255, 0.8)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
        console.log('Quadrant chart initialized with data:', chartData.quadrants.data);
    } catch (error) {
        console.error('Error initializing quadrant chart:', error);
        // Пробуем создать тестовый график
        createTestQuadrantChart(ctx);
    }
}

function createTestQuadrantChart(ctx) {
    console.log('Creating test quadrant chart');
    try {
        quadrantChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Квадрант 1', 'Квадрант 2', 'Квадрант 3', 'Квадрант 4'],
                datasets: [{
                    data: [25, 50, 15, 10],
                    backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%'
            }
        });
        console.log('Test quadrant chart created');
    } catch (error) {
        console.error('Failed to create test quadrant chart:', error);
    }
}

// ============ ИНИЦИАЛИЗАЦИЯ ФИЛЬТРОВ ============
function initFilters() {
    const filterForm = document.getElementById('analytics-filter');
    if (!filterForm) {
        console.error('Filter form not found');
        return;
    }

    // Устанавливаем выбранное значение из URL
    const urlParams = new URLSearchParams(window.location.search);
    const periodParam = urlParams.get('period');
    if (periodParam) {
        const periodSelect = filterForm.querySelector('[name="period"]');
        if (periodSelect) {
            periodSelect.value = periodParam;
            console.log('Set period from URL:', periodParam);
        }
    }

    // Обработка сброса фильтров
    window.resetFilters = function() {
        const periodSelect = filterForm.querySelector('[name="period"]');
        if (periodSelect) periodSelect.value = '30';
        filterForm.submit();
    };
}