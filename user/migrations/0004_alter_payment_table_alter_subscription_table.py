# Generated by Django 4.2.6 on 2023-11-11 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_subscription_payment'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='payment',
            table='user_payment',
        ),
        migrations.AlterModelTable(
            name='subscription',
            table='subscription',
        ),
    ]
