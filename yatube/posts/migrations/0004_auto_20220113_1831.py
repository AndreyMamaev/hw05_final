# Generated by Django 2.2.19 on 2022-01-13 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20220112_2225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='slug',
            new_name='slugurl',
        ),
    ]
