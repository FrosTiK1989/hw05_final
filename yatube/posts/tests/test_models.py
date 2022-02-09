from django.test import TestCase

from ..models import Post, Group, User

AUTHOR = "auth"
GROUP_TITLE = "Тестовая Группа"
GROUP_SLUG = "test-slug"
GROUP_DESCRIPTION = "Тестовое описание"
POST_TEXT = "Тестовый текст"


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_name(self):
        """Тут мы проверям что у моделей корректно работает __str__."""

        group = PostModelTest.group
        name_group = group.title
        self.assertEqual(name_group, str(group))
        post = PostModelTest.post
        post_text = post.text[:15]
        self.assertEqual(post_text, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""

        post = PostModelTest.post
        field_verboses = {
            "text": "Текст поста",
            "pub_date": "Дата Публикации",
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""

        post = PostModelTest.post
        field_help_texts = {
            "text": "Введите текст поста",
            "group": "Выбери группу",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
