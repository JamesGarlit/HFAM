# Generated by Django 5.0.1 on 2024-01-19 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0005_alter_timeout_time_out'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplication',
            name='is_viewed',
            field=models.BooleanField(default=False),
        ),
    ]
