# Generated by Django 4.1.6 on 2024-05-26 18:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0010_delete_leaveapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='online',
            name='acadhead_created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
