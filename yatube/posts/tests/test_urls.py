from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_all_users(self):
        """
        URL-адрес использует соответствующий шаблон и
        Доступен всем пользователям.
        """
        templates_url_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', args=['test-slug']
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=[self.user.username]
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=[self.post.pk]
            ): 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_only_authorized(self):
        """
        URL-адрес использует соответствующий шаблон и доступен
        Только авторизованным.
        """
        templates_url_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', args=[self.post.pk]
            ): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_about_url_exists_at_desired_location(self):
        """Проверка недоступности адреса /unexisting_page/."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_urls_redirect_guest_client(self):
        """Редирект неавторизованного пользователя"""
        post_creat = '/auth/login/?next=/create/'
        post_edit = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        pages = {reverse('posts:post_create'): post_creat,
                 reverse('posts:post_edit', args=[self.post.pk]): post_edit}
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)
