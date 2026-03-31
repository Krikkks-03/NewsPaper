from django.urls import path
from . import views
from .views import (
    NewsListView, ArticlesListView, PostDetailView,
    PostCreateView, PostUpdateView
)

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='news_detail'),

# Поиск
    path('search/', views.news_search, name='news_search'),

# CRUD для новостей
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),

# CRUD для статей
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),

# Профиль (новое)
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('become-author/', views.become_author, name='become_author'),

# Универсальные маршруты для постов (для новых представлений)
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
]