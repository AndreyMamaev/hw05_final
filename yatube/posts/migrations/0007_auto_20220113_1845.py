# Generated by Django 2.2.19 on 2022-01-13 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220113_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.URLField(),
        ),
    ]