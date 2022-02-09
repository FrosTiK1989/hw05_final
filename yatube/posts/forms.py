from django.forms import ModelForm, Textarea, Select
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Что у Вас нового?",
            "group": "Группа, куда постить",
            "image": "Можно прикрепить картинку",
        }
        help_texts = {
            "text": "Поделись своими новостями с нами",
            "group": "Если у тебя есть группа, выбери ее",
            "image": "Картинка будет?",
        }
        widgets = {
            "text": Textarea(
                attrs={
                    "cols": 40,
                    "rows": 10,
                    "class": "form-control",
                    "placeholder": "Текст поста",
                }
            ),
            "group": Select(
                attrs={
                    "class": "form-control",
                    "cols": 40,
                    "rows": 10,
                    "empty": "У тебя нет группы?",
                }
            ),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
