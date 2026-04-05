from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Category, Post, Subscription
from django.contrib.auth.models import User
from django.conf import settings


@shared_task
def send_new_post_notification(post_id):
    """Отправка уведомления подписчикам категории о новой статье"""
    from .models import Post  # локальный импорт для избежания циклических импортов

    post = Post.objects.get(id=post_id)

    for category in post.categories.all():
        subscribers = Subscription.objects.filter(category=category).select_related('user')

        for subscription in subscribers:
            user = subscription.user
            if user.email:
                html_message = render_to_string('emails/new_post_notification.html', {
                    'user': user,
                    'post': post,
                    'category': category,
                    'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'
                })

                send_mail(
                    subject=f'Новая статья в категории "{category.name}"',
                    message=f'Здравствуйте, {user.username}!\n\nВ категории "{category.name}" появилась новая статья: {post.title}\n\nПрочитать: {settings.SITE_URL}/news/{post.id}/',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )


@shared_task
def send_welcome_email(user_id):
    """Отправка приветственного письма при регистрации"""
    user = User.objects.get(id=user_id)

    if user.email:
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'
        })

        send_mail(
            subject='Добро пожаловать в NewsPortal!',
            message=f'Здравствуйте, {user.username}!\n\nСпасибо за регистрацию в нашем новостном портале.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )


@shared_task
def send_weekly_digest():
    """Еженедельная рассылка дайджеста новых статей"""
    one_week_ago = timezone.now() - timedelta(days=7)

    # Получаем все категории с подписчиками
    categories = Category.objects.filter(subscribers__isnull=False).distinct()

    for category in categories:
        new_posts = Post.objects.filter(
            categories=category,
            created_at__gte=one_week_ago
        ).order_by('-created_at')

        if not new_posts.exists():
            continue

        subscribers = Subscription.objects.filter(category=category).select_related('user')

        for subscription in subscribers:
            user = subscription.user
            if user.email:
                html_message = render_to_string('emails/weekly_digest.html', {
                    'user': user,
                    'category': category,
                    'posts': new_posts,
                    'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'
                })

                send_mail(
                    subject=f'Еженедельный дайджест: новые статьи в категории "{category.name}"',
                    message=f'Здравствуйте, {user.username}!\n\nЗа неделю в категории "{category.name}" появилось {new_posts.count()} новых статей.\n\nПосмотреть все: {settings.SITE_URL}/news/',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )