# Generated by Django 4.0.4 on 2022-04-28 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlecomment',
            name='level',
            field=models.IntegerField(blank=True, default=0, verbose_name='Уровень вложенности'),
        ),
    ]