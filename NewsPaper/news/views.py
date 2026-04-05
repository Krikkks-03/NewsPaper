from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author
from .filters import PostFilter
from .forms import ProfileEditForm, PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.contrib import messages
from .models import Category, Subscription
from django.http import JsonResponse


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


# Функция проверки, является ли пользователь автором
def is_author(user):
    return user.groups.filter(name='authors').exists()


# Представление для редактирования профиля (пункт 1)
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'profile_edit.html', {'form': form})


# Представление профиля
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


# Представление для становления автором (пункт 9)
@login_required
def become_author(request):
    user = request.user
    authors_group, _ = Group.objects.get_or_create(name='authors')

    if user.groups.filter(name='authors').exists():
        messages.info(request, 'Вы уже являетесь автором')
    else:
        user.groups.add(authors_group)
        messages.success(request, 'Поздравляем! Теперь вы автор')

    return redirect('profile')


# Класс-представление для списка новостей
class NewsListView(ListView):
    model = Post
    template_name = 'news_list.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(type=Post.NEWS).order_by('-created_at')


# Класс-представление для списка статей
class ArticlesListView(ListView):
    model = Post
    template_name = 'articles_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(type=Post.ARTICLE).order_by('-created_at')


# Класс-представление для детального просмотра поста
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


# Класс-представление для создания новости/статьи (пункты 10, 11)
class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')

    def test_func(self):
        # Проверка прав: пользователь должен быть в группе authors
        return self.request.user.groups.filter(name='authors').exists()

    def form_valid(self, form):
        # Автоматически назначаем автора
        author, _ = Author.objects.get_or_create(user=self.request.user)
        form.instance.author = author
        return super().form_valid(form)


# Класс-представление для редактирования новости/статьи (пункты 10, 11)
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('news_list')

    def test_func(self):
        # Проверка прав: пользователь должен быть автором
        return self.request.user.groups.filter(name='authors').exists()

    def form_valid(self, form):
        # Проверка, что пользователь редактирует свой пост
        if form.instance.author.user != self.request.user:
            messages.error(self.request, 'Вы можете редактировать только свои посты')
            return redirect('post_detail', pk=form.instance.pk)
        return super().form_valid(form)

@login_required
def subscribe_to_category(request, category_id):
    """Подписка пользователя на категорию"""
    category = get_object_or_404(Category, id=category_id)

    # Проверяем, не подписан ли уже
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        category=category
    )

    if created:
        messages.success(request, f'Вы подписались на категорию "{category.name}"')
    else:
        messages.info(request, f'Вы уже подписаны на категорию "{category.name}"')

    return redirect('category_detail', category_id=category.id)

@login_required
def unsubscribe_from_category(request, category_id):
    """Отписка пользователя от категории"""
    category = get_object_or_404(Category, id=category_id)

    Subscription.objects.filter(user=request.user, category=category).delete()
    messages.success(request, f'Вы отписались от категории "{category.name}"')

    return redirect('category_detail', category_id=category.id)

def category_detail(request, category_id):
    """Детальная страница категории с возможностью подписки"""
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(categories=category).order_by('-created_at')

    # Проверяем, подписан ли текущий пользователь
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            user=request.user,
            category=category
        ).exists()

    # Пагинация
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)

    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)

    return render(request, 'news/category_detail.html', {
        'category': category,
        'posts': posts_page,
        'is_subscribed': is_subscribed,
    })