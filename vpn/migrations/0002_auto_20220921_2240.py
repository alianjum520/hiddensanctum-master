# Generated by Django 3.1.6 on 2022-09-21 22:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vpn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='plans',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vpn.plan'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
