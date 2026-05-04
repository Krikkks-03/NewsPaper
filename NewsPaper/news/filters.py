import django_filters
from django import forms
from .models import Post, Category


class PostFilter(django_filters.FilterSet):
    # Фильтр по названию
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'})
    )

    # Фильтр по имени автора
    author_name = django_filters.CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='Имя автора',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя автора'})
    )

    # Фильтр по дате (позже указанной)
    created_at_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Новости после даты',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Фильтр по дате (до указанной)
    created_at_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Новости до даты',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    # Фильтр по типу (новость/статья)
    post_type = django_filters.ChoiceFilter(
        field_name='type',
        choices=Post.TYPE_CHOICES,
        label='Тип поста',
        empty_label='Все типы',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Фильтр по категориям (множественный выбор)
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.all(),
        field_name='categories',
        label='Категории',
        widget=forms.CheckboxSelectMultiple
    )

    # Фильтр по рейтингу (минимальный)
    rating_min = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='gte',
        label='Рейтинг не ниже',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 5'})
    )

    # Фильтр по рейтингу (максимальный)
    rating_max = django_filters.NumberFilter(
        field_name='rating',
        lookup_expr='lte',
        label='Рейтинг не выше',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Например: 100'})
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'author_name',
            'post_type',
            'created_at_after',
            'created_at_before',
            'rating_min',
            'rating_max',
        ]
