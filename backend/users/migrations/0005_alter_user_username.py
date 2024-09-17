# Generated by Django 3.2.3 on 2024-09-17 12:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20240916_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Unacceptable symbol', regex='^[\\w.@+-]+\\Z')], verbose_name='Имя пользователя'),
        ),
    ]