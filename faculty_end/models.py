# faculty_end/models.py
from django.db import models
from admin_end.models import CustomUser, FacultyShift

class LeaveApplication(models.Model):
    LEAVE_TYPES = (
        ('Family', 'Family emergency'),
        ('Medical', 'Medical appointment'),
        ('Extended', 'Extended leave'),
        ('Maternity', 'Maternity leave'),
        ('ChildBirth', 'Child birth'),
        ('Sick', 'Sick leave'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    leave_start_date = models.DateField()
    leave_end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    leave_reason = models.TextField()
    leave_supporting_docs = models.FileField(upload_to='leave_supporting_docs/', null=True, blank=True)

class TimeIn(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    faculty_shift = models.ForeignKey(FacultyShift, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_in = models.TimeField()
    status = models.CharField(max_length=20) # 'On Time', 'Late', 'Early', 'Absent'

class TimeOut(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    faculty_shift = models.ForeignKey(FacultyShift, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    date = models.DateField()
    time_out = models.TimeField()
    status = models.CharField(max_length=20) # 'On Time', 'Late', 'Early', 'Absent'
