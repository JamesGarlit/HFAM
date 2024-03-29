# Generated by Django 4.1.6 on 2024-02-05 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_end', '0020_alter_customuser_extension_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='extension_name',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_middlename',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_picture',
            field=models.ImageField(null=True, upload_to='user_pictures/'),
        ),
    ]
