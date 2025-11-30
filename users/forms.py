# users/forms.py
from django import forms # Импорт модуля форм Django - основа для создания всех форм
from django.contrib.auth.models import User # Импорт стандартной модели пользователя Django
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm # Импорт встроенных форм аутентификации Django
from .models import UserSettings # Импорт кастомной модели настроек пользователя из текущего приложения


# Создание кастомной формы регистрации, наследуемой от стандартной UserCreationForm
class UserRegisterForm(UserCreationForm):
    """
    Форма для регистрации новых пользователей с дополнительными полями
    """

    # Объявление поля email как обязательного поля формы
    email = forms.EmailField(
        # Параметр required=True делает поле обязательным для заполнения
        required=True,
        # Виджет определяет HTML-представление поля
        widget=forms.EmailInput(attrs={
            # CSS класс для стилизации поля
            'class': 'form-control',
            # Текст-подсказка, отображаемая в пустом поле
            'placeholder': 'Введите ваш email'
        })
    )

    # Поле для имени пользователя с ограничением длины
    first_name = forms.CharField(
        # Максимальная длина поля - 30 символов
        max_length=30,
        # Поле обязательно для заполнения
        required=True,
        # Текстовый виджет с кастомными атрибутами
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )

    # Поле для фамилии пользователя
    last_name = forms.CharField(
        max_length=30,
        # required=False - поле необязательное
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вашу фамилию (необязательно)'
        })
    )

    # Класс Meta содержит метаданные о форме
    class Meta:
        # Указываем модель, с которой связана форма
        model = User
        # Список полей модели, которые будут включены в форму
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

        # Виджеты для кастомизации отображения полей модели
        widgets = {
            # Настройка виджета для поля username
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Придумайте имя пользователя'
            }),
        }

    # Конструктор класса - вызывается при создании экземпляра формы
    def __init__(self, *args, **kwargs):
        # Вызов конструктора родительского класса
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        # Обновление атрибутов поля password1 (основной пароль)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте пароль'
        })

        # Обновление атрибутов поля password2 (подтверждение пароля)
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })

    # Метод валидации для поля email
    def clean_email(self):
        # Получение очищенных данных из поля email
        email = self.cleaned_data.get('email')

        # Проверка существования пользователя с таким email в базе данных
        if User.objects.filter(email=email).exists():
            # Выброс исключения валидации если email уже используется
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')

        # Возврат валидного email если проверка пройдена
        return email


# Кастомная форма аутентификации с дополнительной стилизацией
class CustomAuthenticationForm(AuthenticationForm):
    """
    Форма входа в систему с применением CSS классов
    """

    def __init__(self, *args, **kwargs):
        # Вызов конструктора родительского класса AuthenticationForm
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)

        # Настройка атрибутов поля username
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })

        # Настройка атрибутов поля password
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })


# Форма для обновления данных пользователя
class UserUpdateForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя
    """

    # Переопределение поля email с кастомным виджетом
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Поле имени с кастомным виджетом
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Поле фамилии с кастомным виджетом
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        # Используем стандартную модель User
        model = User
        # Поля доступные для редактирования
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            # Виджет для поля username
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Форма для настроек Pomodoro таймера пользователя
class UserSettingsForm(forms.ModelForm):
    """
    Форма настройки параметров Pomodoro таймера
    """

    class Meta:
        # Используем кастомную модель UserSettings
        model = UserSettings
        # Все поля модели включаются в форму
        fields = ['pomodoro_duration', 'short_break_duration', 'long_break_duration', 'pomodoros_before_long_break']

        # Настройка виджетов для числовых полей
        widgets = {
            # Поле длительности Pomodoro (рабочего интервала)
            'pomodoro_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,  # Минимальное значение 1 минута
                'max': 60,  # Максимальное значение 60 минут
            }),
            # Поле длительности короткого перерыва
            'short_break_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,  # Минимальное значение 1 минута
                'max': 30,  # Максимальное значение 30 минут
            }),
            # Поле длительности длинного перерыва
            'long_break_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,  # Минимальное значение 5 минут
                'max': 60,  # Максимальное значение 60 минут
            }),
            # Поле количества Pomodoro до длинного перерыва
            'pomodoros_before_long_break': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,  # Минимальное значение 1 Pomodoro
                'max': 10,  # Максимальное значение 10 Pomodoro
            }),
        }

        # Человеко-читаемые названия полей для отображения в форме
        labels = {
            'pomodoro_duration': 'Длительность Pomodoro (мин)',
            'short_break_duration': 'Короткий перерыв (мин)',
            'long_break_duration': 'Длинный перерыв (мин)',
            'pomodoros_before_long_break': 'Pomodoro до длинного перерыва',
        }

        # Тексты подсказок для полей формы
        help_texts = {
            'pomodoro_duration': 'Стандартное значение: 25 минут',
            'short_break_duration': 'Стандартное значение: 5 минут',
            'long_break_duration': 'Стандартное значение: 15 минут',
            'pomodoros_before_long_break': 'Стандартное значение: 4 Pomodoro',
        }