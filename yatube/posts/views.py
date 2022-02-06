from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Comment, User
from .forms import PostForm, CommentForm
from .utils import get_page_obj


def index(request):
    post_list = Post.objects.all()
    page_obj = get_page_obj(post_list, request.GET.get('page'))

    title = 'Последние обновления на сайте'

    context = {
        'title': title,
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = get_page_obj(post_list, request.GET.get('page'))

    title = f'Записи сообщества {group.description}'

    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)

    title = f'Профайл пользователя {author.get_full_name()}'
    post_list = author.posts.all()
    page_obj = get_page_obj(post_list, request.GET.get('page'))
    context = {
        'title': title,
        'posts_count': post_list.count(),
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    author = post.author
    context = {
        'author': author,
        'posts_count': author.posts.count(),
        'post': post,
        'form': form,
        'user': request.user,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        username = request.user.username

        return redirect('posts:profile', username=username)

    template = 'posts/create_post.html'
    context = {
        'groups': Group.objects.all(),
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post_id)

    template = 'posts/create_post.html'
    context = {
        'is_edit': True,
        'post_id': post_id,
        'post': post,
        'username': request.user,
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
