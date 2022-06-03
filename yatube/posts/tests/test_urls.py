from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def test_page_url_exists_at_desired_location(self):
        """Проверка доступности страниц любому пользователю"""
        code_urls = {
            HTTPStatus.OK: (
                '/',
                f'/group/{PostURLTests.group.slug}/',
                f'/profile/{self.user.username}/',
                f'/posts/{self.post.id}/'
            ),
            HTTPStatus.NOT_FOUND: ('/unexistring_page/',)
        }
        for code, urls in code_urls.items():
            for url in urls:
                with self.subTest(url=url):
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, code)

    def test_page_url_exists_at_desired_location_authorized(self):
        """Проверка доступности страниц авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_url_exists_at_desired_location_authorized_author(self):
        """Проверка доступности страниц автору"""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_404(self):
        """Проверка запроса к несуществующей странице"""
        response = self.guest_client.get('/testnotfound/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_anonymous(self):
        """Проверка редиректа анонимного пользователя"""
        urls = (
            '/create/',
            f'/posts/{self.post.id}/edit/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_urls_uses_correct_template(self):
        """Проверка вызываемых HTML-шаблонов"""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                cache.clear()
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
