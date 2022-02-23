from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.following = User.objects.create_user(username='following')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Это тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комметарий',
            author=cls.user,
            post=cls.post,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.following
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        self.assertEqual(
            post.__str__(), post.text[:15],
            'Метод __str__ модели Post некорректен.'
        )
        self.assertEqual(
            group.__str__(), group.title,
            'Метод __str__ модели Group некорректен.'
        )
        self.assertEqual(
            comment.__str__(), comment.text[:15],
            'Метод __str__ модели Comment некорректен.'
        )

    def test_help_text_for_post(self):
        """Проверяем, что help_text в полях поста совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'pub_date': 'Дата публикации формируется автоматически',
            'author': 'Автор поста записывается автоматически',
            'group': 'Выберите группу',
            'image': 'Выберите картинку',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_for_post(self):
        """Проверяем, что verbose_name в полях поста совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_for_group(self):
        """Проверяем, что help_text в полях группы совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Введите URL группы',
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_for_group(self):
        """Проверяем, что verbose_name в полях группы совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verbose_name = {
            'title': 'Название группы',
            'slug': 'URL группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_for_comment(self):
        """Проверяем, что help_text в полях группы совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_help_texts = {
            'post': 'Пост к которому оставлен комметарий '
            'записывается автоматически',
            'author': 'Автор комментария поста записывается автоматически',
            'text': 'Введите текст комментария',
            'created': 'Дата публикации комментария формируется автоматически',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value
                )

    def test_verbose_name_for_comment(self):
        """Проверяем, что verbose_name в полях группы совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verbose_name = {
            'post': 'Пост к которому оставлен комметарий',
            'author': 'Автор комметария',
            'text': 'Текст комментария',
            'created': 'Дата публикации комментария',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_for_follow(self):
        """Проверяем, что help_text в полях подписки совпадает с ожидаемым."""
        follow = PostModelTest.follow
        field_help_texts = {
            'user': 'Задаётся автоматически аутентифицированный пользователь.',
            'author': 'Задаётся автоматически пользователь '
            'на записи которого подписались.',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).help_text, expected_value
                )

    def test_verbose_name_for_follow(self):
        """Проверяем, что verbose_name в полях подписки
         совпадает с ожидаемым."""
        follow = PostModelTest.follow
        field_verbose_name = {
            'user': 'Подписавшийся пользователь',
            'author': 'Пользователь на которого подписались',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value
                )
