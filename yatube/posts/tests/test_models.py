from django.test import TestCase

from ..models import Group, Post, User, Follow


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(
            username='i-ivanov',
            last_name='Иванов',
            first_name='Иван'
        )
        cls.user_2 = User.objects.create_user(
            username='p-petrov',
            last_name='Петров',
            first_name='Петр'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовое сообщение',
            group=cls.group,
        )
        cls.follow = Follow.objects.create(user=cls.user_1, author=cls.user_2)

    def test_models_group(self):
        group = PostModelTest.group
        self.assertEqual(str(group), 'Тестовая группа')
        self.assertIsInstance(group.title, str)
        self.assertEqual(group.title, 'Тестовая группа')
        self.assertIsInstance(group.slug, str)
        self.assertEqual(group.slug, 'Тестовый слаг')
        self.assertIsInstance(group.description, str)
        self.assertEqual(group.description, 'Тестовое описание')

    def test_models_post(self):
        post = PostModelTest.post
        self.assertEqual(str(post), 'Тестовое сообще')
        self.assertIsInstance(post.text, str)
        self.assertEqual(post.text, 'Тестовое сообщение')
        self.assertIsInstance(post.author, User)
        self.assertEqual(post.author, PostModelTest.user_1)
        self.assertIsInstance(post.group, Group)
        self.assertEqual(post.group, PostModelTest.group)

    def test_models_follow(self):
        follow = PostModelTest.follow
        self.assertEqual(
            str(follow),
            'Иван Иванов подписан на Петр Петров'
        )
        self.assertIsInstance(follow.user, User)
        self.assertEqual(follow.user, PostModelTest.user_1)
        self.assertIsInstance(follow.author, User)
        self.assertEqual(follow.author, PostModelTest.user_2)
