from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text="I am boss of the site.",
            author=User.objects.create(username="superadmin"),
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=User.objects.create(username="boris")
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        comment = PostModelTest.comment
        objects_expected_name = {post: post.text[:15],
                                 group: group.title,
                                 comment: comment.text[:15]}
        for key, value in objects_expected_name.items():
            with self.subTest(key=key):
                self.assertEqual(value, str(key))

    def test_models_help_text(self):
        """
        help_text в полях моделей post и
        comment совпадает с ожидаемым.
        """
        help_post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    help_post._meta.get_field(field).help_text, expected_value)
        help_comment = PostModelTest.comment
        self.assertEqual(
            help_comment._meta.get_field('text').help_text,
            'Текст нового комментария')

    def test_model_post_verbose_name(self):
        """
        verbose_name в полях модели
        post совпадает с ожидаемым.
        """
        verbose_post = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    verbose_post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_model_comment_verbose_name(self):
        """
        verbose_name в полях модели
        comment совпадает с ожидаемым.
        """
        verbose_comment = PostModelTest.comment
        field_verboses = {
            'author': 'Автор',
            'text': 'Текст'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    verbose_comment._meta.get_field(field).verbose_name,
                    expected_value)

    def test_model_follow_verbose_name(self):
        """
        verbose_name в полях модели
        follow совпадает с ожидаемым.
        """
        verbose_follow = PostModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Наблюдаемый'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    verbose_follow._meta.get_field(field).verbose_name,
                    expected_value)
