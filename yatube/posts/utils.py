from typing import Union

from django.core.paginator import Page, Paginator
from django.http import HttpRequest

from yatube.settings import num_posts

from .models import Group, Post, User


def get_paginator(
        posts: Union[Group, Post, User], request: HttpRequest
) -> Page:
    """Функция описывает работу пагинации.
    Создается объект, на вход которого передают список,
    и число элементов которое требуется выводить на одну страницу.
    Выводит полученный список страниц.
    """
    paginator = Paginator(posts, num_posts)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
