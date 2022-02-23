from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Follow, Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.another_user = User.objects.create_user(username='Another')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        objs = [
            Post(
                text=f'Пост №{i}',
                author=cls.user,
                group=cls.group
            )
            for i in range(12)
        ]
        Post.objects.bulk_create(objs=objs)
        # Пост №13 создается с другим автором и без группы
        Post.objects.create(
            text='Пост №13',
            author=cls.another_user,
        )
        cls.follow = Follow.objects.create(
            user=cls.another_user,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='Another')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contains_records(self):
        """Количество постов на страницах index, post_group, profile,
         follow соответствует ожидаемому."""
        paginator_pages = {
            reverse('posts:index'): 10,
            reverse('posts:index') + '?page=2': 3,
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): 10,
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ) + '?page=2': 2,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username}
            ): 10,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username}
            ) + '?page=2': 2,
        }
        for reverse_name, count in paginator_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), count)
        # Проверка follow
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.authorized_client.get(
            reverse('posts:follow_index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 2)
