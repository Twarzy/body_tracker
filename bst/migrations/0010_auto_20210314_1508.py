# Generated by Django 3.1.4 on 2021-03-14 14:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bst', '0009_auto_20210314_1504'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='measurement',
            unique_together={('username', 'date')},
        ),
    ]
