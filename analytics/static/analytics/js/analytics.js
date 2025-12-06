// analytics/static/analytics/js/analytics.js
/**
 * Основной скрипт для модуля аналитики.
 * Обеспечивает интерактивность, переключение вкладок и работу с графиками.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics module loaded');

    // Инициализация всех компонентов
    initNavigation();
    initCharts();
    initFilters();

    // Загружаем дополнительные данные через API
    loadAdditionalData();
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
                    window.dispatchEvent(new Event('resize'));
                }, 100);
            }
        });
    });
}

// ============ ИНИЦИАЛИЗАЦИЯ ГРАФИКОВ ============
function initCharts() {
    // Проверяем наличие Chart.js
    if (typeof Chart === 'undefined') {
        console.error('Chart.js не загружен');
        return;
    }

    // Инициализируем все графики
    initProductivityChart();
    initQuadrantChart();
}

function initProductivityChart() {
    const ctx = document.getElementById('productivityChart');
    if (!ctx) return;

    // Данные из шаблона
    const chartData = window.chartData;
    if (!chartData || !chartData.daily) return;

    new Chart(ctx, {
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
}

function initQuadrantChart() {
    const ctx = document.getElementById('quadrantChart');
    if (!ctx) return;

    const chartData = window.chartData;
    if (!chartData || !chartData.quadrants) return;

    new Chart(ctx, {
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
}

// ============ ИНИЦИАЛИЗАЦИЯ ФИЛЬТРОВ ============
function initFilters() {
    const filterForm = document.getElementById('analytics-filter');
    if (!filterForm) return;

    // Обработка сброса фильтров
    window.resetFilters = function() {
        const periodSelect = filterForm.querySelector('[name="period"]');
        if (periodSelect) periodSelect.value = '30';
        filterForm.submit();
    };
}

// ============ ЗАГРУЗКА ДОПОЛНИТЕЛЬНЫХ ДАННЫХ ============
function loadAdditionalData() {
    // Загружаем данные через API для обновления статистики
    fetchDailyStats();
    fetchQuadrantStats();
}

function fetchDailyStats() {
    const url = '/analytics/api/daily-stats/?days=30';

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Daily stats loaded:', data);
        })
        .catch(error => {
            console.error('Error loading daily stats:', error);
        });
}

function fetchQuadrantStats() {
    const url = '/analytics/api/quadrant-stats/?days=30';

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Quadrant stats loaded:', data);
        })
        .catch(error => {
            console.error('Error loading quadrant stats:', error);
        });
}

// ============ УТИЛИТЫ ============
function updateIndicators(data) {
    // Обновляем счетчики и индикаторы на странице
    const indicators = {
        'total-pomodoros': data.pomodoros ? data.pomodoros.reduce((a, b) => a + b, 0) : 0,
        'total-tasks': data.tasks ? data.tasks.reduce((a, b) => a + b, 0) : 0,
        'avg-productivity': data.productivity ?
            (data.productivity.reduce((a, b) => a + b, 0) / data.productivity.length).toFixed(1) : 0
    };

    // Обновляем DOM элементы
    for (const [key, value] of Object.entries(indicators)) {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = value;
        }
    }
}

function updateQuadrantInfo(data) {
    // Обновляем информацию о распределении по квадрантам
    const quadrantInfo = document.querySelector('.quadrant-distribution-info');
    if (quadrantInfo && data.total_hours) {
        quadrantInfo.innerHTML = `
            <strong>${data.total_hours} часов</strong> работы распределено по квадрантам
        `;
    }
}

// ============ ЭКСПОРТ ДАННЫХ ============
function exportToCSV() {
    const table = document.querySelector('.daily-table');
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('th, td');

        cells.forEach(cell => {
            let text = cell.textContent.trim();
            // Экранируем кавычки
            text = text.replace(/"/g, '""');
            // Оборачиваем в кавычки если содержит запятую
            if (text.includes(',')) {
                text = `"${text}"`;
            }
            rowData.push(text);
        });

        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `analytics_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Добавляем кнопку экспорта
function addExportButton() {
    const header = document.querySelector('.analytics-header');
    if (!header) return;

    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn btn-outline';
    exportBtn.innerHTML = '<span class="icon">📥</span> Экспорт CSV';
    exportBtn.style.marginLeft = 'auto';
    exportBtn.onclick = exportToCSV;

    const actionsContainer = document.createElement('div');
    actionsContainer.style.display = 'flex';
    actionsContainer.style.gap = '1rem';
    actionsContainer.style.alignItems = 'center';
    actionsContainer.appendChild(exportBtn);

    const filterCard = header.querySelector('.filter-card');
    if (filterCard) {
        filterCard.appendChild(actionsContainer);
    }
}

// Инициализируем кнопку экспорта после загрузки
setTimeout(addExportButton, 1000);