# Generated by Django 4.1.1 on 2022-10-02 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0021_blog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='image',
            field=models.ImageField(upload_to='blog_images/'),
        ),
    ]
