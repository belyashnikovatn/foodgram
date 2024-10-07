import logging
import os
from dotenv import load_dotenv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

load_dotenv()
User = get_user_model()

logging.basicConfig(
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


class Command(BaseCommand):
    help = 'Создаёт админа по данным из env файла.'

    def handle(self, *args, **options):

        username = os.getenv('username', 'admin')
        email = os.getenv('email', 'belyashnikova.tn@gmail.com')
        first_name = os.getenv('first_name', 'Tania')
        last_name = os.getenv('last_name', 'B')
        password = os.getenv('password', '12345678')
        avatar = 'profiles/admin.png'

        if not User.objects.filter(username=username).exists():
            logging.info('Создаю аккаунт для %s (%s)' % (username, email))
            try:
                User.objects.create_superuser(
                    email=email, username=username,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    avatar=avatar)
                logging.info('Админ успешно создан.')
            except Exception as error:
                logging.error(f'Ошибка {error}!')
        else:
            logging.info('Админ уже создан.')
