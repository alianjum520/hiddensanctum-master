# Generated by Django 4.1.1 on 2022-09-30 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0016_emailtoken_expired'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='created_at',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]