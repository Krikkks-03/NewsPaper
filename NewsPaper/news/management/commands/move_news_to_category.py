from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from news.models import Post, Category
from django.db import transaction


class Command(BaseCommand):
    help = 'Переносит все новости в указанную категорию с подтверждением'

    def add_arguments(self, parser):
        # Обязательный аргумент: название категории
        parser.add_argument(
            'category_name',
            type=str,
            help='Название категории, в которую будут перенесены все новости'
        )

        # Опциональный аргумент: не запрашивать подтверждение
        parser.add_argument(
            '--force',
            action='store_true',
            help='Выполнить без подтверждения'
        )

        # Опциональный аргумент: сухой запуск (только показать что будет)
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано, без фактического изменения'
        )

    def handle(self, *args, **options):
        category_name = options['category_name']
        force = options['force']
        dry_run = options['dry_run']

        # Находим или создаем категорию
        category, created = Category.objects.get_or_create(name=category_name)

        if created:
            self.stdout.write(self.style.WARNING(f'⚠️ Категория "{category_name}" не существовала и была создана'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Категория "{category_name}" найдена (ID: {category.id})'))

        # Находим все новости (тип 'news')
        news_posts = Post.objects.filter(type='news')
        news_count = news_posts.count()

        if news_count == 0:
            self.stdout.write(self.style.WARNING('⚠️ В базе данных нет ни одной новости'))
            return

        # Показываем информацию о том, что будет сделано
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(f'Будет перенесено новостей: {news_count}')
        self.stdout.write(f'Целевая категория: "{category_name}"')
        self.stdout.write('=' * 50 + '\n')

        # При dry-run показываем первые 5 новостей и выходим
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 РЕЖИМ DRY-RUN: изменения не будут применены\n'))
            self.stdout.write('Первые 5 новостей, которые будут перенесены:')
            for post in news_posts[:5]:
                self.stdout.write(
                    f'  - {post.title} (ID: {post.id}, текущие категории: {list(post.categories.values_list("name", flat=True))})')
            if news_count > 5:
                self.stdout.write(f'  ... и еще {news_count - 5} новостей')
            return

        # Запрашиваем подтверждение (если не указан --force)
        if not force:
            self.stdout.write(self.style.WARNING('⚠️ ВНИМАНИЕ! Это действие изменит категории у всех новостей.'))
            confirm = input('Вы уверены, что хотите продолжить? (да/нет): ')

            if confirm.lower() not in ['да', 'yes', 'y', 'д']:
                self.stdout.write(self.style.ERROR('❌ Операция отменена.'))
                return

        # Выполняем перенос
        try:
            with transaction.atomic():
                updated_count = 0

                for post in news_posts:
                    # Добавляем новость в категорию (если ее там еще нет)
                    if category not in post.categories.all():
                        post.categories.add(category)
                        updated_count += 1

                        # Выводим прогресс каждые 10 новостей
                        if updated_count % 10 == 0 or updated_count == news_count:
                            self.stdout.write(f'  Прогресс: {updated_count}/{news_count}')

                self.stdout.write(self.style.SUCCESS(
                    f'\n Готово! {updated_count} новостей перенесено в категорию "{category_name}"'))

                # Показываем статистику
                self.stdout.write('\n Итоговая статистика:')
                self.stdout.write(
                    f'  - Всего новостей в категории "{category_name}": {Post.objects.filter(categories=category, type="news").count()}')
                self.stdout.write(f'  - Всего категорий в базе: {Category.objects.count()}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при выполнении: {e}'))
            raise CommandError(f'Не удалось выполнить перенос: {e}')