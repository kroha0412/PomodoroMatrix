// core/static/core/js/main.js
// Ждем когда весь HTML документ полностью загрузится и будет готов
document.addEventListener('DOMContentLoaded', function() {
    // Выводим сообщение в консоль браузера для отладки
    console.log('MatrixPomodoro system loaded!');

    // Плавная прокрутка для якорных ссылок (ссылок которые начинаются с #)
    // Находим ВСЕ ссылки у которых атрибут href начинается с #
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    // Для каждой найденной якорной ссылки
    anchorLinks.forEach(link => {
        // Добавляем обработчик события клика
        link.addEventListener('click', function(e) {
            // Отменяем стандартное поведение ссылки (резкий прыжок)
            e.preventDefault();

            // Получаем ID целевого элемента из атрибута href
            const targetId = this.getAttribute('href');
            // Если ссылка ведет просто на # - выходим
            if (targetId === '#') return;

            // Ищем элемент на странице с таким ID
            const targetElement = document.querySelector(targetId);
            // Если элемент найден
            if (targetElement) {
                // Плавно прокручиваем страницу к этому элементу
                targetElement.scrollIntoView({
                    behavior: 'smooth',  // Плавная анимация вместо резкого прыжка
                    block: 'start'       // Выравниваем элемент по верху окна браузера
                });
            }
        });
    });

    // Функция для анимации появления элементов при скролле
    const animateOnScroll = function() {
        // Находим все элементы которые нужно анимировать
        const elements = document.querySelectorAll('.feature-card, .method-card');

        // Для каждого элемента
        elements.forEach(element => {
            // Получаем позицию элемента относительно видимой области окна
            const elementTop = element.getBoundingClientRect().top;
            // Получаем высоту видимой области окна браузера
            const windowHeight = window.innerHeight;

            // Если верхняя граница элемента находится выше низа окна минус 100px
            if (elementTop < windowHeight - 100) {
                // Делаем элемент полностью видимым
                element.style.opacity = '1';
                // Возвращаем элемент на исходную позицию (убираем сдвиг)
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Инициализация анимаций - подготовка элементов перед анимацией
    // Находим все элементы которые будем анимировать
    const animatedElements = document.querySelectorAll('.feature-card, .method-card');
    // Для каждого элемента устанавливаем начальное состояние
    animatedElements.forEach(element => {
        element.style.opacity = '0';                     // Делаем полностью прозрачным
        element.style.transform = 'translateY(30px)';    // Сдвигаем вниз на 30px
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease'; // Настраиваем плавные переходы
    });

    // Добавляем обработчик события скролла - при прокрутке вызываем анимацию
    window.addEventListener('scroll', animateOnScroll);
    // Вызываем функцию сразу при загрузке для элементов которые уже видны
    animateOnScroll();
});