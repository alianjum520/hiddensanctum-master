# Generated by Django 4.1.1 on 2022-09-27 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0010_alter_emailtoken_expiration_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtoken',
            name='token',
            field=models.CharField(max_length=555),
        ),
    ]