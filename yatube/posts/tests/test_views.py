import time
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm, CommentForm
from ..models import Follow, Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_0 = User.objects.create_user(username='NoName')
        cls.user_1 = User.objects.create_user(username='NoNameUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group_uploaded = SimpleUploadedFile(
            name='group_small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user_0,
            text='Тестовый текст',
            image=cls.uploaded,
        )
        # Ожидание в 0.1 секунду чтобы у постов было разное время создания
        time.sleep(0.1)
        cls.post_in_group = Post.objects.create(
            author=cls.user_1,
            text='Пост в группе',
            group=cls.group,
            image=cls.group_uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostViewsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostViewsTests.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostViewsTests.post.pk}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_list_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        second_object = response.context['page_obj'][1]
        # Проверка поля 'post'
        self.assertEqual(first_object, PostViewsTests.post_in_group)
        # Проверка поля 'post' для поста в группе
        self.assertEqual(second_object, PostViewsTests.post)
        # Проверка поля 'index'
        self.assertTrue(response.context['index'])

    def test_posts_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostViewsTests.post_in_group.group.slug}
        ))
        first_object = response.context['page_obj'][0]
        group_object = response.context['group']
        # Проверка поля 'page_obj'
        self.assertEqual(first_object, PostViewsTests.post_in_group)
        # Проверка поля 'group'
        self.assertEqual(group_object, PostViewsTests.post_in_group.group)

    def test_profile_list_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostViewsTests.user_0.username}
        ))
        first_object = response.context['page_obj'][0]
        author_object = response.context['author']
        posts_objects_count = response.context['posts'].count()
        # Проверка поля 'page_obj'
        self.assertEqual(first_object, PostViewsTests.post)
        # Проверка поля 'author'
        self.assertEqual(author_object, PostViewsTests.user_0)
        # Проверка поля 'posts'
        self.assertEqual(
            posts_objects_count, PostViewsTests.user_0.posts.count()
        )
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostViewsTests.user_1.username}
        ))
        first_object = response.context['page_obj'][0]
        # Проверка поля поста в составе группы
        self.assertEqual(first_object, PostViewsTests.post_in_group)
        # Проверка поля 'following'-False
        self.assertTrue(not response.context['following'])
        Follow.objects.create(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        )
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostViewsTests.user_1.username}
        ))
        # Проверка поля 'following'-True
        self.assertTrue(response.context['following'])

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        comment = PostViewsTests.post.comments.create(
            text='Тестовый комментарий',
            author=PostViewsTests.user_0
        )
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostViewsTests.post.pk}
        ))
        post_object = response.context['post']
        comments = response.context['comments']
        form_field = response.context.get('form').fields.get('text')
        # Проверка поля 'form'
        self.assertIsInstance(form_field, forms.fields.CharField)
        self.assertIsInstance(response.context.get('form'), CommentForm)
        # Проверка поля 'post'
        self.assertEqual(post_object, PostViewsTests.post)
        # Проверка поля 'comments'
        self.assertEqual(comments.last(), comment)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostViewsTests.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context.get('form'), PostForm)
        # Проверка поля 'is_edit'
        self.assertTrue(response.context.get('is_edit'))
        # Проверка поля формы 'text'
        self.assertEqual(
            response.context.get('form')['text'].value(),
            PostViewsTests.post.text
        )
        # Проверка поля формы 'group'
        self.assertEqual(
            response.context.get('form')['group'].value(),
            PostViewsTests.post.group
        )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context.get('form'), PostForm)

    def test_posts_list_follow_show_correct_context(self):
        """Шаблон follow сформирован с правильным контекстом."""
        Follow.objects.create(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        # Проверка поля 'post'
        self.assertEqual(first_object, PostViewsTests.post_in_group)
        # Проверка поля 'follow'
        self.assertTrue(response.context['follow'])

    def test_posts_list_follow_create_new_post(self):
        """Новая запись пользователя появляется в ленте тех,
         кто на него подписан."""
        Follow.objects.create(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        # Проверка поcледнего поста на follow_index пользователя user_0
        self.assertEqual(first_object, PostViewsTests.post_in_group)
        # Создание нового поста пользователем user_1
        new_post = Post.objects.create(
            author=PostViewsTests.user_1,
            text='Новый пост',
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        # Проверка поcледнего поста на follow_index пользователя user_0
        self.assertEqual(first_object, new_post)

    def test_posts_list_unfollow_create_new_post(self):
        """Новая запись пользователя не появляется в ленте тех,
         кто на него не подписан."""
        Follow.objects.create(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        # Проверка поcледнего поста на follow_index пользователя user_0
        self.assertEqual(first_object, PostViewsTests.post_in_group)
        # Создание нового поста пользователем user_1
        Post.objects.create(
            author=PostViewsTests.user_0,
            text='Новый пост',
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        # Проверка поcледнего поста на follow_index пользователя user_0
        self.assertEqual(first_object, PostViewsTests.post_in_group)

    def test_follow_view(self):
        """Авторизованный пользователь может подписываться на
         других пользователей."""
        follow_exists = Follow.objects.filter(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        ).exists()
        self.assertFalse(follow_exists)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostViewsTests.user_1.username}
        ))
        follow_exists = Follow.objects.filter(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        ).exists()
        self.assertTrue(follow_exists)

    def test_unfollow_view(self):
        """Авторизованный пользователь может отписываться от пользователей."""
        Follow.objects.create(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostViewsTests.user_1.username}
        ))
        follow_exists = Follow.objects.filter(
            user=PostViewsTests.user_0,
            author=PostViewsTests.user_1
        ).exists()
        self.assertFalse(follow_exists)
