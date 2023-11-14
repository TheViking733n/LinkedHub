# Generated by Django 3.2.21 on 2023-11-10 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('profile_pic', models.TextField()),
                ('bio', models.TextField()),
                ('connections', models.TextField()),
                ('requests', models.TextField()),
                ('post_ids', models.TextField()),
            ],
        ),
    ]