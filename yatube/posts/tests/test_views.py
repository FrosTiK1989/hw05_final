from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Follow, Post, Group, User

ALL_POSTS = 13
POSTS_ON_1ST_PAGE = 10
POSTS_ON_2ND_PAGE = 3
AUTHOR = "auth"
GROUP_TITLE = "Тестовая Группа"
GROUP_SLUG = "test-slug"
GROUP_DESCRIPTION = "Тестовое описание"
POST_TEXT = "Тестовый текст"
POST_CACHE = "Тестовый пост для проверки кэша"


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
            image="posts/small.gif",
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": GROUP_SLUG}
            ): "posts/group_list.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.pk}
            ): "posts/create_post.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): "posts/profile.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_pub_date_0 = first_object.pub_date
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, POST_TEXT)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_image_0, self.post.image, "Беда с картинкой")

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""

        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": self.post.author})
        )
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, POST_TEXT)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(response.context.get("group").title, GROUP_TITLE)
        self.assertEqual(response.context.get("group").slug, GROUP_SLUG)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        )
        self.assertEqual(response.context.get("post").image, self.post.image)
        self.assertEqual(response.context.get("post").text, POST_TEXT)
        self.assertEqual(response.context.get("post").author, self.post.author)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=POST_TEXT,
                    author=cls.user,
                    group=cls.group,
                )
                for i in range(ALL_POSTS)
            ]
        )

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="PopkaDurak")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        reverse_names = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": GROUP_SLUG}),
            reverse("posts:profile", kwargs={"username": AUTHOR}),
        )
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context["page_obj"]),
                    POSTS_ON_1ST_PAGE,
                )

    def test_second_page_contains_three_records(self):
        reverse_names = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": GROUP_SLUG}),
            reverse("posts:profile", kwargs={"username": AUTHOR}),
        )
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + "?page=2")
                self.assertEqual(
                    len(response.context["page_obj"]), POSTS_ON_2ND_PAGE
                )


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.test_post_cache = Post.objects.create(
            author=cls.user,
            text=POST_CACHE,
        )

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="CacheTester")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache_index_page_correct_context(self):
        """Кэш index сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse("posts:index"))
        content = response.content
        context = response.context["page_obj"][0]
        self.assertEqual(context, self.test_post_cache)
        self.test_post_cache.delete()
        response = self.authorized_client.get(reverse("posts:index"))
        new_content = response.content
        self.assertEqual(content, new_content)
        cache.clear()
        response = self.authorized_client.get(reverse("posts:index"))
        new_new_content = response.content
        self.assertNotEqual(content, new_new_content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.test_post = Post.objects.create(
            author=cls.user,
            text=POST_CACHE,
        )

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="Vasiliy")
        self.user2 = User.objects.create_user(username="Alesha")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        cache.clear()

    def test_auth_client_can_follow(self):
        """
        Проверяем что авторизованный пользователь может подписаться на автора.
        """

        follow_count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse("posts:profile_follow", kwargs={"username": AUTHOR})
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": AUTHOR})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

        response = self.authorized_client.get(reverse("posts:follow_index"))
        content = response.content
        response2 = self.authorized_client2.get(reverse("posts:follow_index"))
        new_content = response2.content
        self.assertNotEqual(content, new_content)

    def test_unfollow_auth_client(self):
        """
        Проверяем что можно отписаться от автора и пост исчезнет из избранного.
        """

        response = self.authorized_client.get(
            reverse("posts:profile_unfollow", kwargs={"username": AUTHOR})
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": AUTHOR})
        )
        self.assertEqual(Follow.objects.count(), 0)
