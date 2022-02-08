from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user_reader = User.objects.create_user(username='reader')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовое сообщение',
            group=cls.group,
        )
        cls.public_urls = [
            '/',
            '/group/test-slug/',
            '/profile/author/',
            '/posts/1/',
        ]
        cls.private_urls = [
            '/create/',
            '/posts/1/edit/',
            '/follow/',
        ]
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(StaticURLTests.user_author)
        self.authorized_client_reader = Client()
        self.authorized_client_reader.force_login(StaticURLTests.user_reader)

    def test_static_pages(self):
        for address in StaticURLTests.public_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for address in StaticURLTests.private_urls:
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_redirect(self):
        response = self.authorized_client_reader.get(
            '/posts/1/edit/',
            follow=True
        )
        self.assertRedirects(response, '/posts/1/')

    def test_unknown_page_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        for address, template in StaticURLTests.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)
