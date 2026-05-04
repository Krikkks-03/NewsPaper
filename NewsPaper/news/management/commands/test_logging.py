from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('django')


class Command(BaseCommand):
    help = 'Тестирование логирования'

    def handle(self, *args, **options):
        self.stdout.write('Тестирование логов...')

        logger.debug('Это DEBUG сообщение')
        logger.info('Это INFO сообщение')
        logger.warning('Это WARNING сообщение')
        logger.error('Это ERROR сообщение')

        try:
            raise ValueError('Тестовая ошибка для стэка')
        except ValueError as e:
            logger.critical('Это CRITICAL сообщение с ошибкой', exc_info=True)

        self.stdout.write(self.style.SUCCESS('Логи отправлены!'))