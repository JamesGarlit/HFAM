# Generated by Django 4.1.6 on 2024-05-24 23:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('faculty_end', '0007_complains_has_attachments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complains',
            name='has_attachments',
        ),
        migrations.AddField(
            model_name='complains',
            name='validated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='complains',
            name='validated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='validated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
