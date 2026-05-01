from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import Author, Post
from .tasks import send_welcome_email, send_new_post_notification


@receiver(post_save, sender=User)
def add_user_to_common_group(sender, instance, created, **kwargs):
    """Автоматическое добавление новых пользователей в группу common"""
    if created:
        group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(group)

        # Создаем автора для нового пользователя
        Author.objects.get_or_create(user=instance)

        # Отправляем приветственное письмо
        send_welcome_email.delay(instance.id)

@receiver(post_save, sender=Post)
def notify_subscribers_on_post_creation(sender, instance, created, **kwargs):
    """
    Сигнал, который срабатывает после создания нового поста
    и запускает Celery-задачу для отправки уведомлений подписчикам.
    """
    if created:
        # Запускаем асинхронную задачу для отправки уведомлений
        send_new_post_notification.delay(instance.id)
        print(f"Запущена задача уведомления для поста {instance.id}: {instance.title}")