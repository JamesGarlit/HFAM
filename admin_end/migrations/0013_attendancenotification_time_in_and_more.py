# Generated by Django 4.2.9 on 2024-01-19 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_end', '0012_attendancenotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancenotification',
            name='time_in',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendancenotification',
            name='time_out',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
