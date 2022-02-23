from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..views import CreationForm


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_show_correct_form(self):
        """Шаблон signup сформирован с правильной формой."""
        response = self.guest_client.get(reverse(
            'users:signup'
        ))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(
                    response.context.get('form'), CreationForm
                )
