# Generated by Django 2.2.16 on 2022-02-24 20:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20220224_2331'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique follow',
        ),
    ]