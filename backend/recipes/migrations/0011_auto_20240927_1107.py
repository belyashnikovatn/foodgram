# Generated by Django 3.2.3 on 2024-09-27 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_remove_subscription_unique_subscriptions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipetag',
            options={'verbose_name': 'тэг для рецепта', 'verbose_name_plural': 'Тэги для рецепта'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('user',), 'verbose_name': 'подипска', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('user', 'cooker'), name='unique_user_cooker'),
        ),
    ]
