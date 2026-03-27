import django_filters
from django import forms
from .models import Post


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

    class Meta:
        model = Post
        fields = ['title', 'author_name', 'created_at_after']