# faculty_end/models.py
from django.db import models
from admin_end.models import CustomUser, FacultyShift

class LeaveApplication(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_start_date = models.DateField()
    leave_start_time = models.TimeField()  # New field for leave start time
    leave_end_date = models.DateField()
    leave_end_time = models.TimeField()  # New field for leave end time
    leave_type = models.CharField(max_length=500)
    leave_reason = models.TextField()
    leave_supporting_docs = models.FileField(upload_to='leave_supporting_docs/', null=True, blank=True)
    leave_datetime_submitted = models.DateTimeField(auto_now_add=True)  # New field for submission datetime

class TimeIn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    faculty_shift = models.ForeignKey(FacultyShift, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20)  # 'On Time', 'Late', 'Early', 'Absent'

class TimeOut(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    faculty_shift = models.ForeignKey(FacultyShift, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20) # 'On Time', 'Late', 'Early', 'Absent'
