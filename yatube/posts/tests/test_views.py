from time import sleep

from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_following = User.objects.create_user(username='user1')
        cls.user_follower = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.upload = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        for i in range(14):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый текст',
                image=cls.upload
            )
            sleep(0.01)

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group2,
            text='Тестовый пост №15 группы 2',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.following_client = Client()
        self.follower_client = Client()
        self.following_client.force_login(self.user_following)
        self.follower_client.force_login(self.user_follower)

    def test_pages_uses_correct_template_guest(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.pk}
                    ): 'posts/post_detail.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_authorized(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = PostPagesTests.group
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': group.slug})
        )

        context_post = response.context['page_obj'][0]
        post_author = context_post.author.username
        post_group = context_post.group.title
        post_text = context_post.text
        image_post = context_post.image
        context_group = response.context['group'].title

        self.assertEqual(post_author, 'auth')
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(context_group, 'Тестовая группа')
        self.assertEqual(
            post_text,
            'Тестовый текст'
        )
        self.assertIsInstance(image_post, models.fields.files.ImageFieldFile)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        user = PostPagesTests.user
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': user.username})
        )
        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], self.user)
        self.assertIn('page_obj', response.context)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.pk})
        )

        context_post = response.context['post']
        post_author = context_post.author.username
        post_group = context_post.group.title
        post_text = context_post.text

        self.assertEqual(post_author, 'auth')
        self.assertEqual(post_group, 'Тестовая группа 2')
        self.assertEqual(
            post_text,
            'Тестовый пост №15 группы 2'
        )

    def test_post_create_show_correct_context(self):
        """Шаблон create_post (create) сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post (edit) сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk})
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        context_post_id = response.context['post_id']

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(context_post_id, 15)

    def test_posts_pages_correct_paginator_work(self):
        """Проверка работы паджинатора в шаблонах приложения Posts."""
        group = PostPagesTests.group
        user = PostPagesTests.user
        ONE_PAGE_POSTS = 10

        urls_page2 = {
            reverse('posts:index'): 5,
            reverse('posts:group_list', kwargs={'slug': group.slug}): 4,
            reverse('posts:profile', kwargs={'username': user.username}): 5,
        }

        for page, page_2 in urls_page2.items():
            with self.subTest(page=page):
                pages = {
                    'page': page,
                    '?page=2': page,
                }
                for key, value in pages.items():
                    with self.subTest(key=key):
                        response_page_1 = self.authorized_client.get(value)
                        response_page_2 = self.authorized_client.get(
                            value + key)

                self.assertEqual(
                    len(response_page_1.context['page_obj']),
                    ONE_PAGE_POSTS
                )
                self.assertEqual(
                    len(response_page_2.context['page_obj']),
                    page_2
                )

    def test_post_correct_appear(self):
        """
        Проверка, что созданный пост появится на
        Нужных страницах.
        """
        group2 = PostPagesTests.group2
        user = PostPagesTests.user
        post = PostPagesTests.post

        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': group2.slug}),
            reverse('posts:profile', kwargs={'username': user.username}),
        ]

        for page in pages_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                context_post = response.context['page_obj'][0]

                self.assertEqual(context_post, post)

    def test_post_correct_not_appear(self):
        """
        Проверка, что созданный пост не появится в группе
        К которой не принадлежит.
        """
        group = PostPagesTests.group
        post = PostPagesTests.post
        page = reverse('posts:group_list', kwargs={'slug': group.slug})

        response = self.guest_client.get(page)
        context_post = response.context['page_obj'][0]

        self.assertNotEqual(context_post, post)

    def test_cache(self):
        """Тест кэша."""
        post = Post.objects.create(
            text='text',
            author=self.user,
            group=self.group
        )
        response = self.authorized_client.get(reverse('posts:index'))
        response_post = response.context['page_obj'][0]
        self.assertEqual(post, response_post)
        post.delete()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_3.content)

    def test_follow(self):
        """Зарегистрированный пользователь может подписываться."""
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_follow',
            args=(self.user_following.username,)))
        self.assertEqual(Follow.objects.count(), follower_count + 1)

    def test_unfollow(self):
        """Зарегистрированный пользователь может отписаться."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            args=(self.user_following.username,)))
        self.assertEqual(Follow.objects.count(), follower_count - 1)

    def test_new_post_see_follower(self):
        """Пост появляется в ленте подписавшихся."""
        posts = Post.objects.create(
            text=self.post.text,
            author=self.user_following,
        )
        follow = Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post, posts)
        follow.delete()
        response_2 = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response_2.context['page_obj']), 0)

    def test_users_see_comment(self):
        """
        Комменты правильно отображаются у всех.
        """
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
        )
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, 'Тестовый комментарий')

    def test_add_comment_page_redirects_for_guests(self):
        response = self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.pk}
            ),
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/comment/')
