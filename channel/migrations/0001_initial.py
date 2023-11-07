# Generated by Django 4.2.6 on 2023-11-03 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('link_telemetr', models.URLField()),
            ],
            options={
                'db_table': 'category',
            },
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('link_avatar', models.URLField()),
                ('link_tg', models.URLField()),
            ],
            options={
                'db_table': 'manager',
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('link_avatar', models.URLField()),
                ('link_tg', models.URLField()),
                ('link_telemetr', models.URLField()),
                ('description', models.TextField()),
                ('participants', models.IntegerField()),
                ('views', models.IntegerField()),
                ('views24', models.IntegerField()),
                ('er', models.IntegerField()),
                ('er24', models.IntegerField()),
                ('categories', models.ManyToManyField(to='channel.category')),
                ('managers', models.ManyToManyField(to='channel.manager')),
            ],
            options={
                'db_table': 'channel',
            },
        ),
    ]