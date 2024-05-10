# Generated by Django 4.1.6 on 2024-04-14 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin_end', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeOut',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time_out', models.TimeField(blank=True, null=True)),
                ('status', models.CharField(max_length=20)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_end.academicyear')),
                ('faculty_shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_end.facultyshift')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_end.semester')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimeIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time_in', models.TimeField(blank=True, null=True)),
                ('status', models.CharField(max_length=20)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_end.academicyear')),
                ('faculty_shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_end.facultyshift')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_end.semester')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=100)),
                ('full_name', models.CharField(max_length=150)),
                ('filing_date', models.DateField()),
                ('position', models.CharField(max_length=100)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=15)),
                ('leave_type', models.CharField(max_length=150)),
                ('specify_leavetype', models.CharField(blank=True, max_length=255, null=True)),
                ('leave_details', models.CharField(max_length=150)),
                ('specify_leavedetails', models.CharField(blank=True, max_length=255, null=True)),
                ('days_number', models.CharField(max_length=15)),
                ('commutation', models.CharField(max_length=255)),
                ('inclusive_dates', models.CharField(max_length=255)),
                ('signature', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
