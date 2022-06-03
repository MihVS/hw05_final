import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post, User

NUMBER_OF_POSTS_DISPLAYED = settings.NUMBER_OF_POSTS_DISPLAYED
test_count_post = NUMBER_OF_POSTS_DISPLAYED + 6

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
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        list_posts = []
        for _ in range(test_count_post):
            list_posts.append(
                Post(
                    author=self.user,
                    text=uuid.uuid4(),
                    group=PostURLTests.group
                )
            )
        Post.objects.bulk_create(list_posts)

        self.posts_list = Post.objects.all().select_related('group')

    def _fild_post_equal(self, post_first, post_second, pk):
        self.assertEqual(post_first.text, post_second.get(pk=pk).text)
        self.assertEqual(post_first.group, post_second.get(pk=pk).group)
        self.assertEqual(post_first.author, post_second.get(pk=pk).author)
        self.assertEqual(post_first.image, post_second.get(pk=pk).image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': [
                reverse('posts:index')
            ],
            'posts/group_list.html': [
                reverse(
                    'posts:group_list',
                    kwargs={'slug': PostURLTests.group.slug}
                )
            ],
            'posts/profile.html': [
                reverse(
                    'posts:profile',
                    kwargs={'username': self.user.username}
                )
            ],
            'posts/post_detail.html': [
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': 1}
                )
            ],
            'posts/create_post.html': [
                reverse('posts:post_edit', kwargs={'post_id': 1}),
                reverse('posts:post_create')
            ],
        }
        for template, reverse_names in templates_pages_names.items():
            for reverse_name in reverse_names:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        lists_posts = {
            reverse('posts:index'):
                self.posts_list,
            reverse(
                'posts:group_list', kwargs={'slug': PostURLTests.group.slug}
            ):
                self.posts_list.filter(group__title=PostURLTests.group.title),
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ):
                self.posts_list.filter(group__title=PostURLTests.group.title),
        }
        for reverse_name, posts in lists_posts.items():
            with self.subTest(msg=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_1 = list(response.context['page_obj'])[0]
                self.assertEqual(
                    list(response.context['page_obj']),
                    list(posts[:NUMBER_OF_POSTS_DISPLAYED]),
                    'Переданный context не совпадает с ожидаемым'
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    NUMBER_OF_POSTS_DISPLAYED,
                    'Пагинация работает не правильно'
                )
                self._fild_post_equal(post_1, posts, test_count_post)

    def test_page_post_detail_show_correct_context(self):
        """Шаблон для post_detail.html сформирован с правильным контекстом."""
        id_test_post = 1
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': id_test_post})
        )
        self.assertEqual(response.context['post'],
                         Post.objects.get(pk=id_test_post)
                         )
        self._fild_post_equal(
            response.context['post'],
            self.posts_list,
            id_test_post
        )

    def test_pages_post_create_edit_show_correct_context(self):
        """
        Шаблоны для post_create.html и post_edit.html
        сформированы с правильным контекстом.
        """
        templates_page_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )

        for page in templates_page_names:
            response = self.authorized_client.get(page)
            self.assertTrue(response.context['form'])
            self.assertIsInstance(response.context['form'], PostForm)

    def test_paginator_second_page_contains(self):
        """Проверка количества постов на второй странице"""
        response = self.client.get('?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         test_count_post - NUMBER_OF_POSTS_DISPLAYED)

    def test_show_page_created_post(self):
        """Проверка отображения созданного поста при указанной группе"""
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=PostURLTests.group
        )
        templates_page_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        for page in templates_page_names:
            response = self.authorized_client.get(page)
            with self.subTest(msg=page):
                self.assertEqual(
                    response.context['page_obj'][0], Post.objects.first()
                )

    def test_cash_index(self):
        """Тестирование работы кэша главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            text=uuid.uuid4(),
            group=PostURLTests.group
        )
        response_cash = self.authorized_client.get(reverse('posts:index'))
        cache.clear()
        response_without_cash = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response.content, response_cash.content)
        self.assertNotEqual(response.content, response_without_cash.content)


class FollowTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.client_auth_user = Client()
        self.client_auth_author = Client()
        self.user = User.objects.create_user(username='User')
        self.author = User.objects.create_user(username='Author')
        self.post = Post.objects.create(
            author=self.author,
            text='Тестовый пост для подписчиков'
        )
        self.client_auth_user.force_login(self.user)
        self.client_auth_author.force_login(self.author)

    def _subscribe(self, subscribe: bool, author: str) -> None:
        """
        Метод позволяет подписаться на автора или отписаться
        """
        if subscribe:
            self.client_auth_user.get(
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': author}
                )
            )
        else:
            self.client_auth_user.get(
                reverse(
                    'posts:profile_unfollow',
                    kwargs={'username': author}
                )
            )

    def test_ability_subscribe(self):
        """
        Авторизованный пользователь может подписываться на других пользователей
        """
        self._subscribe(True, self.author)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_ability_unsubscribe(self):
        """
        Авторизованный пользователь может отписаться от других пользователей
        """
        self._subscribe(True, self.author)
        self._subscribe(False, self.author)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_post_in_news_subscriber(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан
        """
        self._subscribe(True, self.author)
        response_subscribe = self.client_auth_user.get(
            reverse('posts:follow_index')
        )
        response_unsubscribe = self.client_auth_author.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(
            response_subscribe.context['page_obj'][0],
            Post.objects.first()
        )
        self.assertEqual(len(response_unsubscribe.context['page_obj']), 0)
