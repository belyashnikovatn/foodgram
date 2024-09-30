# Generated by Django 3.2.3 on 2024-09-30 10:23

from django.db import migrations, models
import foodgram.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20240930_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[foodgram.validators.real_time], verbose_name='Время приготовления (в минутах)'),
        ),
    ]
