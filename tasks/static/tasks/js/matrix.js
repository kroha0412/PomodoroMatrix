// tasks/static/tasks/js/matrix.js
// Основной файл для инициализации всех компонентов матрицы

document.addEventListener('DOMContentLoaded', function() {
    console.log('MatrixPomodoro: Matrix module loaded');

    // Инициализация всех систем происходит автоматически
    // через классы в dragdrop.js и tasks.js

    // Добавляем дополнительные стили для ошибок
    const style = document.createElement('style');
    style.textContent = `
        .form-control.error {
            border-color: #dc3545 !important;
        }

        .notification {
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);
});