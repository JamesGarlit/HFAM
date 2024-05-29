# Generated by Django 4.1.6 on 2024-05-29 07:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0021_alter_timein_acadhead_is_responded'),
    ]

    operations = [
        migrations.AddField(
            model_name='complains',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='evidence',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]