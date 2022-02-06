from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое сообщение',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        current_group = PostModelTest.group
        self.assertEqual(str(current_group), 'Тестовая группа')
        self.assertIsInstance(current_group.title, str)
        self.assertEqual(current_group.title, 'Тестовая группа')
        self.assertIsInstance(current_group.slug, str)
        self.assertEqual(current_group.slug, 'Тестовый слаг')
        self.assertIsInstance(current_group.description, str)
        self.assertEqual(current_group.description, 'Тестовое описание')

        current_post = PostModelTest.post
        self.assertEqual(str(current_post), 'Тестовое сообще')
        self.assertIsInstance(current_post.text, str)
        self.assertEqual(current_post.text, 'Тестовое сообщение')
        self.assertIsInstance(current_post.author, User)
        self.assertEqual(current_post.author, PostModelTest.user)
        self.assertIsInstance(current_post.group, Group)
        self.assertEqual(current_post.group, current_group)
