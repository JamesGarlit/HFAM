# Generated by Django 4.1.6 on 2024-04-14 18:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_end', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplicationaction',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
