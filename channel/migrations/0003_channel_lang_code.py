# Generated by Django 4.2.6 on 2023-11-03 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0002_alter_category_title_alter_manager_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='lang_code',
            field=models.CharField(default='any', max_length=5),
        ),
    ]
