from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Author
from .filters import PostFilter
from .forms import PostForm


def news_list(request):
    # Получаем все новости (тип 'news')
    posts = Post.objects.filter(type='news').order_by('-created_at')

    # Пагинация
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)

    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    # Генерация диапазона страниц для отображения
    current_page = posts_page.number
    num_pages = paginator.num_pages

    # Показываем до 3 страниц слева и справа от текущей
    left_range = max(1, current_page - 3)
    right_range = min(num_pages, current_page + 3)
    page_range = range(left_range, right_range + 1)

    return render(request, 'news/news_list.html', {
        'articles': posts_page,
        'paginator': paginator,
        'page_range': page_range,
        'current_page': current_page,
        'num_pages': num_pages,
    })


def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'news/news_detail.html', {'article': post})


def news_search(request):
    # все посты
    posts = Post.objects.all().order_by('-created_at')

    # Применяем фильтры
    post_filter = PostFilter(request.GET, queryset=posts)
    filtered_posts = post_filter.qs

    # Пагинация для результатов поиска
    paginator = Paginator(filtered_posts, 10)
    page = request.GET.get('page', 1)

    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    # Диапазон страниц
    current_page = posts_page.number
    num_pages = paginator.num_pages
    left_range = max(1, current_page - 3)
    right_range = min(num_pages, current_page + 3)
    page_range = range(left_range, right_range + 1)

    return render(request, 'news/news_search.html', {
        'filter': post_filter,
        'articles': posts_page,
        'paginator': paginator,
        'page_range': page_range,
        'current_page': current_page,
        'num_pages': num_pages,
    })


# CRUD для новостей
@login_required
def news_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.type = 'news'
            # Получаем или создаем автора для текущего пользователя
            author, created = Author.objects.get_or_create(user=request.user)
            post.author = author
            post.save()
            messages.success(request, 'Новость успешно создана!')
            return redirect('news_detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'news/post_form.html', {
        'form': form,
        'title': 'Создание новости',
    })


@login_required
def news_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, type='news')

    # Проверка прав: только автор может редактировать
    if post.author.user != request.user:
        messages.error(request, 'Вы не можете редактировать эту новость')
        return redirect('news_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Новость успешно обновлена!')
            return redirect('news_detail', pk=pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'news/post_form.html', {
        'form': form,
        'title': 'Редактирование новости',
    })


@login_required
def news_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, type='news')

    # Проверка прав
    if post.author.user != request.user:
        messages.error(request, 'Вы не можете удалить эту новость')
        return redirect('news_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Новость успешно удалена!')
        return redirect('news_list')

    return render(request, 'news/post_confirm_delete.html', {
        'post': post,
        'title': 'Удаление новости'
    })


# CRUD для статей
@login_required
def article_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.type = 'article'
            author, created = Author.objects.get_or_create(user=request.user)
            post.author = author
            post.save()
            messages.success(request, 'Статья успешно создана!')
            return redirect('news_detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'news/post_form.html', {
        'form': form,
        'title': 'Создание статьи',
    })


@login_required
def article_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, type='article')

    if post.author.user != request.user:
        messages.error(request, 'Вы не можете редактировать эту статью')
        return redirect('news_detail', pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья успешно обновлена!')
            return redirect('news_detail', pk=pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'news/post_form.html', {
        'form': form,
        'title': 'Редактирование статьи',
    })


@login_required
def article_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, type='article')

    if post.author.user != request.user:
        messages.error(request, 'Вы не можете удалить эту статью')
        return redirect('news_detail', pk=pk)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Статья успешно удалена!')
        return redirect('news_list')

    return render(request, 'news/post_confirm_delete.html', {
        'post': post,
        'title': 'Удаление статьи'
    })