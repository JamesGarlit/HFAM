# Generated by Django 4.1.6 on 2024-05-29 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0023_remove_complains_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workedhours',
            name='user',
        ),
        migrations.DeleteModel(
            name='TimeOut',
        ),
        migrations.DeleteModel(
            name='WorkedHours',
        ),
    ]
