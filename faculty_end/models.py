from django.db import models
from admin_end.models import CustomUser
from django.utils import timezone

class TimeIn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    time_in = models.TimeField(blank=True, null=True)
    time_start = models.TimeField(blank=True, null=True) 
    time_out = models.TimeField(blank=True, null=True)
    day = models.CharField(max_length=50)
    date = models.DateField(blank=True, null=True)
    month = models.CharField(max_length=255)
    delay = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50)
    coursesection = models.CharField(max_length=50)
    remarks = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=timezone.now) 
    is_absent = models.BooleanField(default=False)

class Online(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    time_in = models.TimeField(blank=True, null=True)
    time_start = models.TimeField(blank=True, null=True) 
    time_out = models.TimeField(blank=True, null=True)
    day = models.CharField(max_length=50)
    date = models.DateField(blank=True, null=True)
    month = models.CharField(max_length=255)
    delay = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50)
    coursesection = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
    is_absent = models.BooleanField(default=False)
    is_red_instruction = models.BooleanField(default=False)
    has_attachments = models.BooleanField(default=False)



class TimeOut(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=50) # Early, Late, On Time
    created_at = models.DateTimeField(default=timezone.now) 

class WorkedHours(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)


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


class OnlineEvidence(models.Model):
    online = models.ForeignKey(Online, related_name='online_evidence', on_delete=models.CASCADE, null=True, blank=True)
    evidence = models.ImageField(upload_to='evidence_images/', blank=True, null=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(default=timezone.now)

