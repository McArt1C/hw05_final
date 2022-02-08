from http import HTTPStatus

from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from ..models import Group, Post, User, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        test_posts_number = 13
        cls.user1 = User.objects.create_user(
            username='test-user-1',
            first_name='Имя',
            last_name='Фамилия'
        )
        cls.user2 = User.objects.create_user(username='test-user-2')
        cls.user3 = User.objects.create_user(username='test-user-3')
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug-1',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание',
        )
        cls.posts = []
        for i in range(test_posts_number):
            new_post = Post.objects.create(
                author=(cls.user1 if i < 2 else cls.user2),
                text=f'Пост {i + 1}',
                group=(cls.group1 if i > 10 else cls.group2),
            )
            cls.posts.append(new_post)
        cls.templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug-1'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'test-user-1'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
                'posts/create_post.html',
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user1)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(PostPagesTests.user2)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(PostPagesTests.user3)

    def test_views_use_correct_templates(self):
        templates_pages = PostPagesTests.templates_pages_names.items()
        for reverse_name, template in templates_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_has_correct_context(self):
        all_posts = Post.objects.all()
        reverse_name = reverse('posts:index')
        expected = {
            'title':
                'Последние обновления на сайте',
            'page_obj':
                [post for post in all_posts][:settings.POSTS_PER_PAGE],
        }
        self.finish_test_for_pages_with_post_list(reverse_name, expected)

    def tests_group_posts_has_correct_context(self):
        test_group = PostPagesTests.group1
        test_group_posts = Post.objects.filter(group=test_group)
        reverse_name = reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug-1'}
        )
        expected = {
            'group': test_group,
            'title': 'Записи сообщества Тестовое описание',
            'page_obj':
                [post for post in test_group_posts][:settings.POSTS_PER_PAGE],
        }
        self.finish_test_for_pages_with_post_list(reverse_name, expected)

    def test_profile_has_correct_context(self):
        test_user = PostPagesTests.user1
        reverse_name = reverse(
            'posts:profile',
            kwargs={'username': 'test-user-1'}
        )
        expected = {
            'title': 'Профайл пользователя Имя Фамилия',
            'posts_count': test_user.posts.all().count(),
            'author': test_user,
            'page_obj':
                [post for post in Post.objects.filter(
                    author=PostPagesTests.user1)][:settings.POSTS_PER_PAGE],
        }
        self.finish_test_for_pages_with_post_list(reverse_name, expected)

    def test_post_detail_has_correct_context(self):
        test_user = PostPagesTests.user1
        reverse_name = reverse('posts:post_detail', kwargs={'post_id': 1})
        expected = {
            'author': test_user,
            'posts_count': test_user.posts.all().count(),
            'post': Post.objects.get(pk=1)
        }
        self.finish_test_for_pages_with_post_list(reverse_name, expected)

    def test_post_create_has_correct_context(self):
        reverse_name = reverse('posts:post_create')
        form_fields = {
            'title': type(None),
            'group': forms.fields.ChoiceField,
        }
        self.finish_form_check(reverse_name, form_fields)

    def test_post_edit_has_correct_context(self):
        reverse_name = reverse('posts:post_edit', kwargs={'post_id': 1})
        form_fields = {
            'title': type(None),
            'group': forms.fields.ChoiceField,
        }
        self.finish_form_check(reverse_name, form_fields)
        expected = {
            'is_edit': True,
            'post_id': 1,
            'username': PostPagesTests.user1
        }
        self.finish_test_for_pages_with_post_list(reverse_name, expected)

    def test_first_page_contains_ten_records(self):
        reverse_names_and_posts = {
            reverse('posts:index'): 10,
            reverse('posts:group_list', kwargs={'slug': 'test-slug-2'}): 10,
            reverse('posts:profile', kwargs={'username': 'test-user-2'}): 10,
        }
        for reverse_name, expected in reverse_names_and_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_correct_records(self):
        reverse_names_and_posts = {
            reverse('posts:index'): 3,
            reverse('posts:group_list', kwargs={'slug': 'test-slug-2'}): 1,
            reverse('posts:profile', kwargs={'username': 'test-user-2'}): 1,
        }
        for reverse_name, expected in reverse_names_and_posts.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_new_post_in_correct_places(self):
        author = PostPagesTests.user1
        correct_group = PostPagesTests.group1
        incorrect_group = PostPagesTests.group2
        all_posts = Post.objects.all()
        all_posts_count = all_posts.count()
        group1_posts_count = all_posts.filter(group=correct_group).count()
        group2_posts_count = all_posts.filter(group=incorrect_group).count()
        author_posts_count = all_posts.filter(author=author).count()
        Post.objects.create(
            author=PostPagesTests.user1,
            text='Последний пост',
            group=PostPagesTests.group1,
        )
        self.assertEqual(all_posts.count(),
                         all_posts_count + 1)
        self.assertEqual(all_posts.filter(group=correct_group).count(),
                         group1_posts_count + 1)
        self.assertEqual(all_posts.filter(group=incorrect_group).count(),
                         group2_posts_count)
        self.assertEqual(all_posts.filter(author=author).count(),
                         author_posts_count + 1)

    def test_index_page_cache(self):
        new_post = Post.objects.create(
                author=PostPagesTests.user1,
                text=f'Пост для проверки кэша',
            )
        response = self.authorized_client.get(reverse('posts:index'))
        context_page_after_creating_post = response.context['page_obj']
        content_after_creating_post = response.content
        self.assertIn(new_post, context_page_after_creating_post)

        new_post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        content_after_deleting_post = response.content
        self.assertEqual(
            content_after_creating_post,
            content_after_deleting_post
        )

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        content_after_clearing_cache = response.content
        self.assertNotEqual(
            content_after_creating_post,
            content_after_clearing_cache
        )

    def test_authorized_user_can_follow_and_unfollow(self):
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'test-user-2'}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'test-user-2'}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_guest_cant_follow(self):
        self.guest_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'test-user-2'}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_appears_at_followers(self):
        self.authorized_client2.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'test-user-1'}
            )
        )
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 2)
        response = self.authorized_client3.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def finish_test_for_pages_with_post_list(self, reverse_name, expected):
        response = self.authorized_client.get(reverse_name)
        for (key, value) in expected.items():
            if key == 'page_obj':
                context = response.context.get(key).object_list
            else:
                context = response.context.get(key)
            self.assertEqual(context, value)

    def finish_form_check(self, reverse_name, form_fields):
        response = self.guest_client.get(reverse_name)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.authorized_client.get(reverse_name)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
