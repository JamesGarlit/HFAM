# Generated by Django 5.0 on 2024-01-16 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0004_alter_timein_time_in'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeout',
            name='time_out',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
