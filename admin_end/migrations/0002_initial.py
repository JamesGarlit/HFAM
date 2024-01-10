# Generated by Django 5.0 on 2024-01-10 10:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('admin_end', '0001_initial'),
        ('faculty_end', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='approval',
            name='leave_application',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='faculty_end.leaveapplication'),
        ),
        migrations.AddField(
            model_name='facultyshift',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculty_shifts', to=settings.AUTH_USER_MODEL),
        ),
    ]
