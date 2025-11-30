# users/urls.py
from django.urls import path # Импорт функции path для определения URL-маршрутов
from . import views # Импорт views (представления) из текущего приложения users
from django.contrib.auth import views as auth_views # Импорт встроенных представлений аутентификации Django с псевдонимом для избежания конфликта имен

# Определение пространства имен приложения для использования в шаблонах и коде
app_name = 'users'

# Список URL-маршрутов приложения users
urlpatterns = [
    # Маршрут для регистрации нового пользователя
    # URL: /users/register/
    path('register/', views.register, name='register'),

    # Маршрут для входа в систему (кастомное представление)
    # URL: /users/login/
    path('login/', views.custom_login, name='login'),

    # Маршрут для выхода из системы (кастомное представление)
    # URL: /users/logout/
    path('logout/', views.custom_logout, name='logout'),

    # Маршрут для просмотра и редактирования профиля пользователя
    # URL: /users/profile/
    path('profile/', views.profile, name='profile'),

    # --- ВОССТАНОВЛЕНИЕ ПАРОЛЯ ---

    # Маршрут для запроса сброса пароля
    # URL: /users/password-reset/
    path('password-reset/',
         # Использование встроенного представления сброса пароля
         auth_views.PasswordResetView.as_view(
             # Указание кастомного шаблона для формы сброса пароля
             template_name='users/password_reset_form.html',
             # Указание кастомного шаблона для email сообщения
             email_template_name='users/password_reset_email.html',
             # URL для перенаправления после успешного запроса
             success_url='/users/password-reset/done/'
         ),
         name='password_reset'),

    # Маршрут для страницы подтверждения отправки email
    # URL: /users/password-reset/done/
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             # Указание кастомного шаблона для информационной страницы
             template_name='users/password_reset_info.html',
             # Передача дополнительного контекста в шаблон
             extra_context={'page_type': 'email_sent'}  # ← Параметр для определения типа страницы
         ),
         name='password_reset_done'),

    # Маршрут для подтверждения сброса пароля (с uidb64 и токеном)
    # URL: /users/reset/<uidb64>/<token>/
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             # Использование того же шаблона, что и для запроса сброса
             template_name='users/password_reset_form.html',
             # URL для перенаправления после успешного сброса пароля
             success_url='/users/reset/done/'
         ),
         name='password_reset_confirm'),

    # Маршрут для страницы успешного сброса пароля
    # URL: /users/reset/done/
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             # Указание кастомного шаблона для информационной страницы
             template_name='users/password_reset_info.html',
             # Передача дополнительного контекста в шаблон
             extra_context={'page_type': 'password_changed'}  # ← Параметр для определения типа страницы
         ),
         name='password_reset_complete'),
]