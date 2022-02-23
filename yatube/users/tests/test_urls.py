from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_urls_for_guest_client(self):
        """URL-адрес доступен для неавторизаванного пользователя."""
        urls = [
            '/auth/login/', '/auth/signup/',
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_unexisting_page(self):
        """URL-адрес несуществующей страницы недоступен."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_users_urls_for_authorized_client(self):
        """URL-адрес доступен для авторизаванного пользователя."""
        urls = [
            '/auth/password_change/',
            '/auth/password_change/done/', '/auth/password_reset/',
            '/auth/password_reset/done/', '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/', '/auth/logout/',
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
