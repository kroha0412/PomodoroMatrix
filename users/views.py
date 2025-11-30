# users/views.py
from django.shortcuts import render, redirect  # Функции для рендеринга шаблонов и перенаправления
from django.contrib import messages  # Система сообщений для пользователя
from django.contrib.auth import login, logout, authenticate  # Функции аутентификации
from django.contrib.auth.decorators import login_required  # Декоратор для ограничения доступа
from .forms import UserRegisterForm, UserUpdateForm, UserSettingsForm, \
    CustomAuthenticationForm  # Кастомные формы приложения


def register(request):
    """
    Представление для регистрации новых пользователей.
    Обрабатывает GET и POST запросы для создания нового аккаунта.
    """
    # Проверка: если пользователь уже авторизован, перенаправляем его
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы в системе.')
        return redirect('core:home')

    # Обработка POST запроса (отправка формы регистрации)
    if request.method == 'POST':
        # Создаем экземпляр формы с данными из запроса
        form = UserRegisterForm(request.POST)

        # Проверяем валидность формы
        if form.is_valid():
            # Сохраняем пользователя в базу данных
            user = form.save()
            # Получаем очищенные данные из формы
            username = form.cleaned_data.get('username')
            # Показываем сообщение об успехе
            messages.success(
                request,
                f'Аккаунт {username} успешно создан! Теперь вы можете войти в систему.'
            )
            # Перенаправляем на страницу входа
            return redirect('users:login')
        else:
            # Если форма невалидна, показываем ошибку
            messages.error(
                request,
                'Пожалуйста, исправьте ошибки в форме.'
            )
    else:
        # GET запрос - создаем пустую форму
        form = UserRegisterForm()

    # Рендерим шаблон с формой
    return render(request, 'users/register.html', {'form': form})


def custom_login(request):
    """
    Кастомное представление для входа в систему.
    Заменяет стандартное представление Django для большей гибкости.
    """
    # Проверка: если пользователь уже авторизован, перенаправляем его
    if request.user.is_authenticated:
        messages.info(request, 'Вы уже авторизованы в системе.')
        return redirect('core:home')

    # Обработка POST запроса (отправка формы входа)
    if request.method == 'POST':
        # Используем нашу кастомную форму аутентификации
        form = CustomAuthenticationForm(request, data=request.POST)

        # Проверяем валидность формы
        if form.is_valid():
            # Получаем очищенные данные из формы
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Аутентифицируем пользователя
            user = authenticate(username=username, password=password)

            # Если пользователь существует и данные верны
            if user is not None:
                # Выполняем вход пользователя
                login(request, user)
                # Закомментировано сообщение об успешном входе (возможно, чтобы не загромождать интерфейс)
                # messages.success(
                #     request,
                #     f'Добро пожаловать, {username}! Вы успешно вошли в систему.'
                # )

                # Получаем параметр 'next' для перенаправления или используем значение по умолчанию
                next_page = request.GET.get('next', 'core:home')
                return redirect(next_page)
            else:
                # Ошибка аутентификации (редкий случай, когда форма валидна, но authenticate вернул None)
                messages.error(request, 'Ошибка аутентификации.')
        else:
            # Форма невалидна - неправильные учетные данные
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        # GET запрос - создаем пустую форму аутентификации
        form = CustomAuthenticationForm()

    # Рендерим шаблон входа с формой
    return render(request, 'users/login.html', {'form': form})


def custom_logout(request):
    """
    Представление для выхода из системы.
    Выполняет logout и перенаправляет на главную страницу.
    """
    # Выход пользователя из системы
    logout(request)
    # Закомментировано сообщение об успешном выходе
    # messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('core:home')


@login_required  # Декоратор гарантирует, что только авторизованные пользователи имеют доступ
def profile(request):
    """
    Представление для просмотра и редактирования профиля пользователя.
    Обрабатывает две формы: основные данные пользователя и настройки Pomodoro.
    """
    # Обработка POST запроса (отправка формы редактирования)
    if request.method == 'POST':
        # Определяем какая форма была отправлена с помощью скрытого поля 'form_type'
        if 'form_type' in request.POST:

            # Обработка формы основных данных пользователя
            if request.POST['form_type'] == 'user_info':
                # Создаем форму с данными из запроса и текущим экземпляром пользователя
                user_form = UserUpdateForm(request.POST, instance=request.user)
                # Создаем форму настроек только для отображения (не для сохранения)
                settings_form = UserSettingsForm(instance=request.user.usersettings)

                # Проверяем валидность формы основных данных
                if user_form.is_valid():
                    # Сохраняем изменения пользователя
                    user_form.save()
                    messages.success(request, 'Ваши данные успешно обновлены!')
                    return redirect('users:profile')
                # Если форма невалидна, продолжит выполнение и покажет формы с ошибками

            # Обработка формы настроек Pomodoro
            elif request.POST['form_type'] == 'user_settings':
                # Создаем форму основных данных только для отображения
                user_form = UserUpdateForm(instance=request.user)
                # Создаем форму настроек с данными из запроса
                settings_form = UserSettingsForm(
                    request.POST,
                    instance=request.user.usersettings
                )

                # Проверяем валидность формы настроек
                if settings_form.is_valid():
                    # Сохраняем настройки
                    settings_form.save()
                    messages.success(request, 'Настройки Pomodoro успешно обновлены!')
                    return redirect('users:profile')
                # Если форма невалидна, продолжит выполнение и покажет формы с ошибками
        else:
            # Если form_type не указан, создаем обе формы заново с текущими данными
            user_form = UserUpdateForm(instance=request.user)
            settings_form = UserSettingsForm(instance=request.user.usersettings)
    else:
        # GET запрос - создаем формы с текущими данными пользователя
        user_form = UserUpdateForm(instance=request.user)
        settings_form = UserSettingsForm(instance=request.user.usersettings)

    # Подготавливаем контекст для шаблона
    context = {
        'user_form': user_form,  # Форма основных данных
        'settings_form': settings_form,  # Форма настроек Pomodoro
    }

    # Рендерим шаблон профиля
    return render(request, 'users/profile.html', context)