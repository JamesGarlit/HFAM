# Generated by Django 4.1.6 on 2024-05-29 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0027_complains_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='complains',
            name='type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]