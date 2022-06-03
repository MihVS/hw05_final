from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import get_page_paginator


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all().select_related('group')
    paginator = get_page_paginator(post_list, request)
    return render(request, template, context=paginator)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    group_list = group.groups.all()
    paginator = get_page_paginator(group_list, request)
    context = {
        'group': group,
        **paginator
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    user = request.user
    post_list = author.posts.all().select_related('author')
    paginator = get_page_paginator(post_list, request)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'user': user,
        'following': following,
        **paginator
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id).select_related('post')
    paginator = get_page_paginator(comments, request)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        **paginator
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    context = {
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.text = form.cleaned_data['text']
        post.group = form.cleaned_data['group']
        post.author = request.user
        post.save()
        return redirect('posts:post_edit', post_id)
    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id
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


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    list_of_posts = Post.objects.filter(author__following__user=request.user)
    paginator = get_page_paginator(list_of_posts, request)
    return render(request, template, context=paginator)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username)
