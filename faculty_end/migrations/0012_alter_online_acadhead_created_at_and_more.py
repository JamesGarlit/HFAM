# Generated by Django 4.1.6 on 2024-05-26 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0011_online_acadhead_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='online',
            name='acadhead_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='online',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]