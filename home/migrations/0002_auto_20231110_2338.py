# Generated by Django 3.2.21 on 2023-11-10 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='connections',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='post_ids',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_pic',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='requests',
            field=models.TextField(blank=True),
        ),
    ]
