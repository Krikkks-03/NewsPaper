from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Register your models here.
from .models import Author, Category, Post, PostCategory, Comment

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Comment)


# Настройка прав в админке
def setup_groups_and_permissions():
    """Создание групп и назначение прав (вызвать в migration или shell)"""

    # Создаем группу common
    common_group, _ = Group.objects.get_or_create(name='common')
    common_group.permissions.clear()  # у common нет специальных прав

    # Создаем группу authors
    authors_group, _ = Group.objects.get_or_create(name='authors')

    # Получаем права на модель Post
    content_type = ContentType.objects.get_for_model(Post)

    # Права на создание и редактирование
    permissions = [
        Permission.objects.get(codename='add_post', content_type=content_type),
        Permission.objects.get(codename='change_post', content_type=content_type),
    ]

    # Назначаем права группе authors
    authors_group.permissions.set(permissions)

# Вызываем функцию для создания групп
setup_groups_and_permissions()