from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from .models import Follow, Post, Group, get_user_model
from .forms import PostForm, CommentForm

POSTS_ON_PAGE = 10

User = get_user_model()


def get_paginator_page(request, query_set):
    paginator = Paginator(query_set, POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.all()
    page_obj = get_paginator_page(request, posts)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_paginator_page(request, posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_paginator_page(request, posts)
    user = request.user
    if (
        user.is_authenticated
        and author != user
        and Follow.objects.filter(user=user, author=author).exists()
    ):
        following = True
    else:
        following = False
    context = {
        "author": author,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    form = CommentForm()
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    context = {
        "post": post,
        "form": form,
        "comments": comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, template, {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", username=post.author)


@login_required
def post_edit(request, post_id):
    template = "posts/create_post.html"
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if not form.is_valid():
        context = {
            "form": form,
            "post_id": post_id,
            "is_edit": True,
        }
        return render(request, template, context)
    post = form.save(commit=False)
    post.save(update_fields=["text", "group", "image"])
    return redirect("posts:post_detail", post_id)


@login_required
def comment_added(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    user = request.user
    authors = user.follower.all().values("author")
    posts = Post.objects.filter(author__in=authors)
    page_obj = get_paginator_page(request, posts)
    context = {
        "page_obj": page_obj,
    }

    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    if request.user != author and not following.exists():
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect("posts:profile", username=author)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=user).delete()
    return redirect("posts:profile", username=author)
