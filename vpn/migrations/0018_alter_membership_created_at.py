# Generated by Django 4.1.1 on 2022-10-01 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0017_membership_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
