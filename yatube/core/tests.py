from django.test import Client, TestCase
from http import HTTPStatus


class CoreTest(TestCase):
    """Проверка страницы 404"""
    def setUp(self):
        self.guest_client = Client()

    def test_uses_template_not_found(self):
        response = self.guest_client.get('/not-found-page/')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
