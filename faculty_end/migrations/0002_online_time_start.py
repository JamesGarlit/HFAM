# Generated by Django 4.1.6 on 2024-05-23 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='online',
            name='time_start',
            field=models.TimeField(blank=True, null=True),
        ),
    ]