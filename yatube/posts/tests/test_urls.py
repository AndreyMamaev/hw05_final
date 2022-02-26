from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from django.urls import reverse

from ..models import Follow, Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Это тестовый пост',
        )
        cls.another_user = User.objects.create_user(username='Another')
        cls.another_post = Post.objects.create(
            author=cls.another_user,
            text='Это ещё один тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/follow/': 'posts/follow.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            (
                f'/posts/{PostURLTests.post.pk}/'
            ): 'posts/post_detail.html',
            (
                f'/posts/{PostURLTests.post.pk}/edit/'
            ): 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_for_guest_client(self):
        """URL-адрес доступен для неавторизаванного пользователя."""
        urls = [
            '/', f'/group/{PostURLTests.group.slug}/',
            f'/profile/{PostURLTests.user.username}/',
            f'/posts/{PostURLTests.post.pk}/',
            '/about/author/', '/about/tech/',
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_unexisting_page(self):
        """URL-адрес несуществующей страницы недоступен."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_for_authorized_client(self):
        """URL-адрес доступен для авторизаванного пользователя."""
        urls = [
            f'/posts/{PostURLTests.post.pk}/edit/', '/create/',
            '/follow/',
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_guest_client(self):
        """При попытке изменения и комментирования
         поста, а также попытке подписки, отписки и просмотра записей
          интересных пользователей происходит редирект на login."""
        urls = [
            f'/posts/{PostURLTests.post.pk}/edit/', '/create/',
            f'/posts/{PostURLTests.post.pk}/comment/',
            f'/profile/{PostURLTests.post.author.username}/follow/',
            f'/profile/{PostURLTests.post.author.username}/unfollow/',
            '/follow/'
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(
                    response, f'/auth/login/?next={address}'
                )

    def test_redirect_for_not_author_client(self):
        """При попытке изменения поста не его автором происходит
         редирект на post_detail."""
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.another_post.pk}/edit/'
        )
        self.assertRedirects(
            response, f'/posts/{PostURLTests.another_post.pk}/'
        )

    def test_redirect_follow(self):
        """При подписке и отписке от автора происходит
         редирект на profile."""
        response = self.authorized_client.get(
            f'/profile/{PostURLTests.another_user.username}/follow/'
        )
        self.assertRedirects(
            response, f'/profile/{PostURLTests.another_user.username}/'
        )
        response = self.authorized_client.get(
            f'/profile/{PostURLTests.another_user.username}/unfollow/'
        )
        self.assertRedirects(
            response, f'/profile/{PostURLTests.another_user.username}/'
        )

    def test_index_page_cache(self):
        """Главная страница кэшируется"""
        cache.clear()
        post = Post.objects.create(
            text='Тест кэша',
            author=PostURLTests.user
        )
        response = self.guest_client.get(reverse('posts:index'))
        cache_check = response.content
        post.delete()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_check)
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_check)

    def test_follow_page_cache(self):
        """Страница follow кэшируется"""
        cache.clear()
        post = Post.objects.create(
            text='Тест кэша',
            author=PostURLTests.another_user
        )
        Follow.objects.create(
            user=PostURLTests.user,
            author=PostURLTests.another_user
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        cache_check = response.content
        post.delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(response.content, cache_check)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(response.content, cache_check)

    def test_follow_and_unfollow_url(self):
        """Авторизованный пользователь может подписываться на
         других пользователей и удалять их из подписок."""
        follow_exists = Follow.objects.filter(
            user=PostURLTests.user,
            author=PostURLTests.another_user
        ).exists()
        self.assertFalse(follow_exists)
        self.authorized_client.get(
            f'/profile/{PostURLTests.another_user.username}/follow/'
        )
        follow_exists = Follow.objects.filter(
            user=PostURLTests.user,
            author=PostURLTests.another_user
        ).exists()
        self.assertTrue(follow_exists)
        self.authorized_client.get(
            f'/profile/{PostURLTests.another_user.username}/unfollow/'
        )
        follow_exists = Follow.objects.filter(
            user=PostURLTests.user,
            author=PostURLTests.another_user
        ).exists()
        self.assertFalse(follow_exists)
