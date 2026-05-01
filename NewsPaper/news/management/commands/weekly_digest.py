from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from NewsPaper.news.models import Post, Category, Subscription
from django.conf import settings


class Command(BaseCommand):
    help = 'Отправляет еженедельный дайджест подписчикам'

    def handle(self, *args, **options):
        one_week_ago = timezone.now() - timedelta(days=7)

        categories = Category.objects.filter(subscribers__isnull=False).distinct()

        for category in categories:
            new_posts = Post.objects.filter(
                categories=category,
                created_at__gte=one_week_ago
            )

            if not new_posts.exists():
                continue

            subscribers = Subscription.objects.filter(category=category).select_related('user')

            for sub in subscribers:
                if sub.user.email:
                    posts_list = '\n'.join([f'- {p.title}: {p.preview()}' for p in new_posts[:5]])

                    send_mail(
                        subject=f'Еженедельный дайджест: {category.name}',
                        message=f'Здравствуйте, {sub.user.username}!\n\nНовые статьи за неделю:\n{posts_list}\n\nЧитать все: {settings.SITE_URL}/news/',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[sub.user.email],
                        fail_silently=False,
                    )

            self.stdout.write(self.style.SUCCESS(f'Дайджест отправлен для категории "{category.name}"'))

        self.stdout.write(self.style.SUCCESS('Еженедельная рассылка завершена'))