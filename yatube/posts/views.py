from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_paginator
from typing import Union
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse


def index(request):
    posts = Post.objects.select_related('author', 'group')
    context = {'page_obj': get_paginator(posts, request)}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    context = {
        'group': group,
        'page_obj': get_paginator(posts, request)
    }
    return render(request, 'posts/group_list.html', context)


# использование select_related, рефакторинг функции group_posts

# def group_posts(request, slug):
#     group = get_object_or_404(Group, slug=slug)
#     posts = group.gr_posts.select_related('author', 'group')
#     context = {
#         'group': group,
#         'page_obj': get_paginator(posts, request)
#     }
#     return render(request, 'posts/group_list.html', context)


def profile(request, username, following=False):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author')
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
    context = {
        'author': author,
        'following': following,
        'page_obj': get_paginator(post_list, request)
    }
    return render(request, 'posts/profile.html', context)


# использование полиформизма, рефакторинг функции profile

# def is_following(author, user):
#     return Follow.objects.filter(author=author, user=user).exists()

# def profile(request, username):
#     author = get_object_or_404(User, username=username)
#     post_list = author.posts.select_related('author')

#     following = False
#     if request.user.is_authenticated:
#         following = is_following(author, request.user)

#     context = {
#         'author': author,
#         'following': following,
#         'page_obj': get_paginator(post_list, request)
#     }
#     return render(request, 'posts/profile.html', context)


# реализация паттерна итератор для функции profile (строка 79-110)

# class PostIterator:
#     def __init__(self, user):
#         self.posts = user.posts.select_related('author')
#         self.index = 0

#     def __iter__(self):
#         return self

#     def __next__(self):
#         if self.index < len(self.posts):
#             post = self.posts[self.index]
#             self.index += 1
#             return post
#         else:
#             raise StopIteration


# @login_required
# def profile(request, username):
#     author = get_object_or_404(User, username=username)
#     post_iterator = PostIterator(author)  # Создаем итератор по постам автора
#     if request.user.is_authenticated:
#         following = Follow.objects.filter(
#             author=author,
#             user=request.user
#         ).exists()
#     context = {
#         'author': author,
#         'page_obj': post_iterator,
#         'following': following,
#     }
#     return render(request, 'posts/profile.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST,
        files=request.FILES or None,
    )
    if not request.method == 'POST' or not form.is_valid():
        return render(request,
                      'posts/create_post.html',
                      {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user)


# использование аннотирования функции,
# рефакторинг функции post_create

# @login_required
# def post_create(request: HttpRequest) -> Union[HttpResponse,
#                                                TemplateResponse]:
#     form = PostForm(
#         request.POST,
#         files=request.FILES or None,
#     )
#     if not request.method == 'POST' or not form.is_valid():
#         return render(request,
#                       'posts/create_post.html',
#                       {'form': form})
#     post = form.save(commit=False)
#     post.author = request.user
#     post.save()
#     return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    postedit = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=postedit
    )
    if postedit.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  context={'form': form,
                           'is_edit': True,
                           'post_id': post_id})


# использование полиформизма, альтернативная функция post_edit

# def is_author(post, user):
#     return post.author == user


# @login_required
# def post_edit(request, post_id):
#     postedit = get_object_or_404(Post, pk=post_id)
#     form = PostForm(
#         request.POST or None,
#         files=request.FILES or None,
#         instance=postedit
#     )
#     if is_author(postedit, request.user) and form.is_valid():
#         form.save()
#         return redirect('posts:post_detail', post_id)
#     return render(request, 'posts/create_post.html',
#                   context={'form': form,
#                            'is_edit': True,
#                            'post_id': post_id})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

# без вызова оператора @, декорирование выглядело бы так
# add_comment = login_required(add_comment)


@login_required
def follow_index(request):
    post = (
        Post.objects
        .select_related('author')
        .filter(author__following__user=request.user)
    )
    page_obj = get_paginator(post, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(
            user=request.user,
            author=author,
    ).exists() and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
