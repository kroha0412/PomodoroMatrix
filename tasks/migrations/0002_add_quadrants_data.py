from django.db import migrations


def add_initial_quadrants(apps, schema_editor):
    """
    Функция для добавления начальных данных в таблицу EisenhowerQuadrant.
    apps - объект, содержащий исторические версии моделей
    schema_editor - объект для работы с схемой БД
    """
    # Получаем модель EisenhowerQuadrant в ее текущем состоянии
    EisenhowerQuadrant = apps.get_model('tasks', 'EisenhowerQuadrant')

    # Создаем список квадрантов с данными
    quadrants_data = [
        {
            'name': 'Квадрант 1: Важные и срочные',
            'description': 'Задачи, которые требуют немедленного внимания. Кризисы, дедлайны, проблемы.',
            'priority_order': 1,
            'color_code': '#FF6B6B',  # Красный
            'icon': 'urgency'
        },
        {
            'name': 'Квадрант 2: Важные и несрочные',
            'description': 'Стратегические задачи для долгосрочного развития. Планирование, обучение, отношения.',
            'priority_order': 2,
            'color_code': '#4ECDC4',  # Бирюзовый
            'icon': 'strategy'
        },
        {
            'name': 'Квадрант 3: Срочные и неважные',
            'description': 'Отвлекающие факторы. Некоторые звонки, встречи, незначительные дела.',
            'priority_order': 3,
            'color_code': '#45B7D1',  # Голубой
            'icon': 'distraction'
        },
        {
            'name': 'Квадрант 4: Несрочные и неважные',
            'description': 'Пустая трата времени. Соцсети, бесцельный серфинг, тривиальные занятия.',
            'priority_order': 4,
            'color_code': '#96CEB4',  # Зеленый
            'icon': 'waste'
        }
    ]

    # Создаем записи в базе данных
    for quadrant_data in quadrants_data:
        # Создаем объект модели, но не сохраняем его сразу
        quadrant = EisenhowerQuadrant(**quadrant_data)
        # Сохраняем объект в базу данных
        quadrant.save()


def remove_initial_quadrants(apps, schema_editor):
    """
    Функция для отката миграции - удаляет все квадранты.
    Эта функция выполняется при отмене миграции.
    """
    EisenhowerQuadrant = apps.get_model('tasks', 'EisenhowerQuadrant')
    # Удаляем все записи из таблицы EisenhowerQuadrant
    EisenhowerQuadrant.objects.all().delete()


class Migration(migrations.Migration):
    # Зависимости от предыдущих миграций
    dependencies = [
        ('tasks', '0001_initial'),  # Зависит от первой миграции приложения tasks
    ]

    operations = [
        # Запускаем нашу функцию при применении миграции
        migrations.RunPython(
            add_initial_quadrants,  # Функция для применения
            remove_initial_quadrants  # Функция для отката
        ),
    ]