# Generated by Django 4.2.6 on 2023-11-03 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0005_alter_channel_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manager',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='manager',
            name='link_avatar',
            field=models.TextField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='manager',
            name='link_tg',
            field=models.TextField(max_length=500),
        ),
    ]
