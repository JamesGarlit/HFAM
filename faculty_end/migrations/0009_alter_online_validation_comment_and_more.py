# Generated by Django 4.1.6 on 2024-05-25 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_end', '0008_remove_complains_has_attachments_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='online',
            name='validation_comment',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='timein',
            name='validation_comment',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
