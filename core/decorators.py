# core/decorators.py
"""
Декораторы для контроля доступа к страницам.
"""

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def anonymous_required(view_func):
    """
    Декоратор для страниц, доступных только НЕавторизованным пользователям.
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:methods_guide')  # Редирект на инструкцию для авторизованных
        return view_func(request, *args, **kwargs)
    return wrapper

def authenticated_required(view_func):
    """
    Декоратор для страниц, доступных только авторизованным пользователям.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper