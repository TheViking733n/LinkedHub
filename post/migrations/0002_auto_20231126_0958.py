# Generated by Django 3.2.21 on 2023-11-26 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.IntegerField()),
                ('item_type', models.CharField(max_length=10)),
                ('user_id', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='post',
            name='comment_ids',
        ),
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
    ]
