# Generated by Django 4.1.1 on 2022-09-28 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0015_alter_emailtoken_expiration_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtoken',
            name='expired',
            field=models.BooleanField(default=False),
        ),
    ]
