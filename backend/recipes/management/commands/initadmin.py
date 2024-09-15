from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):

        username = 'admin'
        email = 'belyashnikova.tn@gmail.com'
        first_name = 'Tania'
        last_name = 'B'
        password = 'admin12345678'

        if not User.objects.filter(username=username).exists():
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username,
                first_name=first_name,
                last_name=last_name,
                password=password)
        else:
            print('Admin account has already been initialized.')
