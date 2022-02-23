import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.pk,
            'image': PostCreateFormTests.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostCreateFormTests.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        self.post = Post.objects.create(
            text='Тестовый текст',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
            image=PostCreateFormTests.uploaded,
        )
        new_uploaded = SimpleUploadedFile(
            name='new_small.gif',
            content=PostCreateFormTests.small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'image': new_uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
                group=None,
                author=PostCreateFormTests.user,
                image='posts/new_small.gif'
            ).exists()
        )

    def test_guest_client_create_post(self):
        """Неавторизованный пользователь пытается создать запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_client_create_comment(self):
        """Неавторизованный пользователь пытается
         создать комментарий к посту."""
        post = Post.objects.create(
            text='Тестовый пост',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
        )
        comment_count = post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{post.pk}/comment/'
        )
        self.assertEqual(post.comments.count(), comment_count)

    def test_guest_authorized_create_comment(self):
        """Авторизованный пользователь создает комментарий к посту."""
        post = Post.objects.create(
            text='Тестовый пост',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
        )
        comment_count = post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, f'/posts/{post.pk}/')
        self.assertEqual(post.comments.count(), comment_count + 1)
        self.assertTrue(
            post.comments.filter(
                text='Тестовый комментарий',
                author=PostCreateFormTests.user,
                post=post,
            ).exists()
        )
