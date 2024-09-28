import os
from dotenv import load_dotenv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

load_dotenv()
User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):

        username = os.getenv('username', 'admin')
        email = os.getenv('email', 'belyashnikova.tn@gmail.com')
        first_name = os.getenv('first_name', 'Tania')
        last_name = os.getenv('last_name', 'B')
        password = os.getenv('password', '12345678')

        if not User.objects.filter(username=username).exists():
            print('Создаю аккаунт для %s (%s)' % (username, email))
            User.objects.create_superuser(
                email=email, username=username,
                first_name=first_name,
                last_name=last_name,
                password=password)
        else:
            print('Админ уже создан.')
