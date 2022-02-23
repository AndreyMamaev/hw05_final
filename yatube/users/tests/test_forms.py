import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SignUpFormTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        """Валидная форма создает запись в User."""
        user_count = User.objects.count()
        form_data = {
            'first_name': 'Name',
            'last_name': 'Last',
            'username': 'test_username',
            'email': 'example@mail.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Name',
                last_name='Last',
                username='test_username',
                email='example@mail.com',
            ).exists()
        )
