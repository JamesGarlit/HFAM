# Generated by Django 4.1.6 on 2024-05-23 18:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0003_timein_course_timein_section_alter_timein_delay_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timein',
            old_name='course',
            new_name='coursesection',
        ),
        migrations.RemoveField(
            model_name='timein',
            name='section',
        ),
        migrations.AddField(
            model_name='online',
            name='coursesection',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]