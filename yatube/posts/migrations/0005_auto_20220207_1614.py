# Generated by Django 2.2.16 on 2022-02-07 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_follow'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='user_author'),
        ),
    ]
