import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        list_group = []
        for number in range(1, 4):
            list_group.append(
                Group(
                    title=f'Тестовая группа {number}',
                    slug=f'test-slug-{number}',
                    description=f'Тестовое описание {number}',
                )
            )
        Group.objects.bulk_create(list_group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=Group.objects.get(title='Тестовая группа 1')
        )

    def test_create_posts(self):
        """Пост создаётся при отправке валидной формы"""
        post_count = Post.objects.count()
        group = Group.objects.get(title='Тестовая группа 2')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый тестовый пост',
            'group': group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый пост',
                author=self.user.id,
                group=group,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_posts(self):
        """Изменение поста с post_id в базе данных"""
        post_id = self.post.id
        group_3 = Group.objects.get(title='Тестовая группа 3')
        form_data = {
            'text': 'Изменённый тестовый пост',
            'group': group_3.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
        )
        self.assertRedirects(response, reverse(
            'posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTrue(
            Post.objects.filter(
                text='Изменённый тестовый пост',
                id=post_id,
                group=group_3
            ).exists()
        )

    def test_guest_client_cant_create_post(self):
        """Не авторизированный пользователь не может создавать пост"""
        post_count = Post.objects.count()
        group = Group.objects.get(title='Тестовая группа 1')
        form_data = {
            'text': 'Новый тестовый пост',
            'group': group.id,
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_client_cant_create_comment(self):
        """Не авторизированный пользователь не может создавать комментарий"""
        comment_count = Comment.objects.count()
        post_id = self.post.id
        form_data = {
            'text': 'Новый тестовый комментарий',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_create_comment(self):
        """После успешной отправки комментарий появляется на странице поста"""
        comment_count = Comment.objects.count()
        post_id = self.post.id
        form_data = {
            'text': 'Новый тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post_id}),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Новый тестовый комментарий',
            ).exists(),
            'Созданный пост не соответствует ожидаемому'
        )

