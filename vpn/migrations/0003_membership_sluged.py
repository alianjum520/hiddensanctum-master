# Generated by Django 3.1.6 on 2022-09-21 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0002_auto_20220921_2240'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='sluged',
            field=models.CharField(default=2, max_length=1000),
            preserve_default=False,
        ),
    ]
