// analytics/static/analytics/js/analytics.js
/**
 * Скрипт для упрощенной аналитики
 * Только график продуктивности
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics dashboard loaded');
    initCharts();
    initFilters();
});

// ============ ГРАФИК ============
function initCharts() {
    if (typeof Chart === 'undefined') {
        // Если Chart.js еще не загружен, пробуем снова через 100мс
        setTimeout(initCharts, 100);
        return;
    }

    if (!window.chartData) {
        console.error('Chart data not found');
        return;
    }

    createProductivityChart();
}

function createProductivityChart() {
    const ctx = document.getElementById('productivityChart');
    if (!ctx) return;

    const data = window.chartData;

    try {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.daily.labels,
                datasets: [
                    {
                        label: 'Продуктивность',
                        data: data.daily.productivity,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Фокус',
                        data: data.daily.focus,
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
    } catch (error) {
        console.error('Error creating productivity chart:', error);
    }
}

// ============ ФИЛЬТРЫ ============
function initFilters() {
    const filterForm = document.getElementById('analytics-filter');
    if (!filterForm) return;

    const urlParams = new URLSearchParams(window.location.search);
    const periodParam = urlParams.get('period');
    if (periodParam) {
        const periodSelect = filterForm.querySelector('[name="period"]');
        if (periodSelect) periodSelect.value = periodParam;
    }
}