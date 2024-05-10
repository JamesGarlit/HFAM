# faculty_end/models.py
from django.db import models
from admin_end.models import CustomUser

class TimeIn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=50)

class TimeOut(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=50)

class LeaveApplication(models.Model):
    user = models.ForeignKey('admin_end.CustomUser', on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    full_name = models.CharField(max_length=150)
    filing_date = models.DateField()
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=15, decimal_places=2)
    leave_type = models.CharField(max_length=150)
    specify_leavetype = models.CharField(max_length=255, blank=True, null=True)
    leave_details = models.CharField(max_length=150)
    specify_leavedetails = models.CharField(max_length=255, blank=True, null=True)
    days_number = models.CharField(max_length=15)
    commutation = models.CharField(max_length=255)
    inclusive_dates = models.CharField(max_length=255)
    signature = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True) 

