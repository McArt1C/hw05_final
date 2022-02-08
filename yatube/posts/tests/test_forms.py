from http import HTTPStatus
import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 1',
            group=cls.group,
        )
        cls.expected_text = 'Тестовый пост 2'
        cls.expected_comment = 'Тестовый комментарий'
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_1 = SimpleUploadedFile(
            name='small_1.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.form_data_1 = {
            'group': 1,
            'text': 'Тестовый пост 2',
            'image': cls.uploaded_1,
        }
        cls.form_data_2 = {
            'group': 1,
            'text': 'Тестовый пост 2',
            'image': cls.uploaded_2,
        }
        cls.comment_form = {
            'text': 'Тестовый комментарий'
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=PostCreateFormTests.form_data_1,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'test-user'})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=PostCreateFormTests.expected_text,
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group
            ).exists()
        )

    def test_edit_post(self):
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=PostCreateFormTests.form_data_2,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        current_post = Post.objects.get(pk=1)
        self.assertEqual(current_post.text, PostCreateFormTests.expected_text)
        self.assertEqual(current_post.group, PostCreateFormTests.group)
        self.assertEqual(current_post.author, PostCreateFormTests.user)

    def test_guest_cant_comment(self):
        comments_count = PostCreateFormTests.post.comments.count()
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=PostCreateFormTests.comment_form,
            follow=True
        )
        self.assertEqual(
            PostCreateFormTests.post.comments.count(),
            comments_count
        )

    def test_authorized_can_comment(self):
        comments_count = PostCreateFormTests.post.comments.count()
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=PostCreateFormTests.comment_form,
            follow=True
        )
        self.assertEqual(
            PostCreateFormTests.post.comments.count(),
            comments_count + 1
        )
