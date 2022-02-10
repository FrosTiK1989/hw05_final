from django.test import TestCase, Client

from ..models import Post, Group, User

from http import HTTPStatus

AUTHOR = "auth"
GROUP_TITLE = "Тестовая Группа"
GROUP_SLUG = "test-slug"
GROUP_DESCRIPTION = "Тестовое описание"
POST_TEXT = "Тестовый текст"


class PostURLTest(TestCase):
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
        )
        cls.templates_public_url_names = {
            "/": "posts/index.html",
            f"/profile/{cls.user}/": "posts/profile.html",
            f"/posts/{cls.post.pk}/": "posts/post_detail.html",
            "/group/test-slug/": "posts/group_list.html",
        }
        cls.templates_private_urls_names = {
            "/create/": "posts/create_post.html",
            f"/posts/{cls.post.pk}/edit/": "posts/create_post.html",
        }
        cls.custom_pages_url_names = {
            "/unexisting_page/": "core/404.html",
        }

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user2 = User.objects.create_user(username="TestUsver")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_publiq_page_exists_at_desired_location(self):
        """Проверка публичных страниц."""

        for address, template in self.templates_public_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f"Страница {template} не фурычит",
                )
                self.assertTemplateUsed(response, template)

    def test_private_page_exists_at_login_user(self):
        """Проверка приватных страниц доступных поьзователям сайта."""

        for address, template in self.templates_private_urls_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f"Страница {template} не фурычит",
                )
                self.assertTemplateUsed(response, template)

    def test_custom_page(self):
        """Проверка кастомных страниц."""

        for address, template in self.custom_pages_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                    f"Страница {template} не фурычит",
                )
                self.assertTemplateUsed(response, template)

    def test_redirect_page(self):
        """Проверка редиректов"""

        response = self.guest_client.get("/create/")
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
            "Страница создания поста не доступна",
        )

    def test_not_found_page(self):
        """Запрашиваемая страница не найдена."""

        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
