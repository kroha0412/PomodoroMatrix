// tasks/static/tasks/js/dragdrop.js
class DragDropManager {
    constructor() {
        console.log('DragDropManager initialized');
        // Основная логика теперь в tasks.js
    }
}

// Для обратной совместимости
document.addEventListener('DOMContentLoaded', () => {
    new DragDropManager();
});