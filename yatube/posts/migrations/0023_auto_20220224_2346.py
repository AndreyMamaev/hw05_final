# Generated by Django 2.2.16 on 2022-02-24 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0022_auto_20220224_2345'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique follow'),
        ),
    ]
