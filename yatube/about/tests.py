from django.test import Client, TestCase
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_url_exists_at_desired_location(self):
        """Проверка доступности адресов статичных страниц."""
        urls = (
            '/about/author/',
            '/about/tech/'
        )
        for url in urls:
            with self.subTest(msg=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_static_pages_url_uses_correct_template(self):
        """Проверка шаблона для статичных страниц."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in templates_url_names.items():
            response = self.guest_client.get(url)
            with self.subTest(msg=url):
                self.assertTemplateUsed(response, template)