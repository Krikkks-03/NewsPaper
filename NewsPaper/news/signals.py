from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import Author


@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    """Автоматическое добавление новых пользователей в группу common"""
    if created:
        group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(group)

        # Создаем автора для нового пользователя
        Author.objects.get_or_create(user=instance)