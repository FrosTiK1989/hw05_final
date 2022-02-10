import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..forms import PostForm, CommentForm
from ..models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

GROUP_TITLE = "Тестовая Группа"
GROUP_SLUG = "test-slug"
GROUP_DESCRIPTION = "Тестовое описание"
POST_TEXT = "Тестовый текст"
POST_TEXT_EDIT = "Тестовый текст БЛА БЛА БЛА"
AUTHOR = "auth"
PICTURE = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
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
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.user2 = User.objects.create_user(username="Marmok")
        self.non_author = Client()
        self.non_author.force_login(self.user2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_post_create(self):
        post_count = Post.objects.count()
        small_gif = PICTURE
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif",
        )
        form_data = {
            "text": POST_TEXT,
            "title": GROUP_TITLE,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": AUTHOR}),
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=POST_TEXT,
                image="posts/small.gif",
            ).exists()
        )

    def test_post_edit(self):
        new_post = Post.objects.create(
            text="New text for new test",
            author=self.user,
        )
        form_data = {
            "text": POST_TEXT_EDIT,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": new_post.pk}),
            data=form_data,
            follow=True,
        )
        new_post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": new_post.pk}),
        )
        self.assertEqual(new_post.text, POST_TEXT_EDIT, "Не состыковки")
        self.assertTrue(
            Post.objects.filter(
                id=new_post.pk,
                text=POST_TEXT_EDIT,
            ).exists()
        )

    def test_post_edit_non_author(self):
        """Пост не может изменить не автор поста."""

        new_post_non = Post.objects.create(
            text="New text for new test non author",
            author=self.user,
        )
        form_data_non = {
            "text": POST_TEXT_EDIT,
        }
        response = self.non_author.post(
            reverse("posts:post_edit", kwargs={"post_id": new_post_non.pk}),
            data=form_data_non,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": new_post_non.pk}),
        )
        self.assertNotEqual(new_post_non.text, POST_TEXT_EDIT, "Не состыковки")


class TestCommentForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username="DimaKuplinov")
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_add_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            "text": "Test Comment",
        }

        response = self.authorized_client.post(
            reverse("posts:comment_added", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
            id=self.post.pk,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}),
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.pk,
                text=POST_TEXT,
                comments=comment,
            ).exists()
        )
        response = self.guest_client.post(
            reverse("posts:comment_added", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
            id=self.post.pk,
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next=/posts/{comment.id}/comment/',
        )
        self.assertEqual(Comment.objects.count(), Comment.objects.count())
