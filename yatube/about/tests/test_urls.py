from django.test import TestCase, Client

from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_aboutpage(self):
        """Тестируем AboutPage."""

        response = self.guest_client.get("/about/author/")
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            "Страница о тебе не работает",
        )

    def test_author_url_uses_correct_template(self):
        """Проверка шаблона для адреса /about/author/."""

        response = self.guest_client.get("/about/author/")
        self.assertTemplateUsed(response, "about/author.html")

    def test_techpage(self):
        """Тестируем TechPage."""

        response = self.guest_client.get("/about/tech/")
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            "Страница о технологиях не работает",
        )

    def test_tech_url_uses_correct_template(self):
        """Проверяем что используется корректный шаблон tech."""

        response = self.guest_client.get("/about/tech/")
        self.assertTemplateUsed(
            response, "about/tech.html", "Шаблон не корректный"
        )
