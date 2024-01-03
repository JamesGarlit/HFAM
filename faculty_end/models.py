# faculty_end/models.py
from django.db import models
from admin_end.models import CustomUser

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

class Place(models.Model):
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.location

class Arrival(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    time_in = models.TimeField()
    time_in_date = models.DateField()

    def __str__(self):
        return f"{self.user.get_full_name()} arrived at {self.place} on {self.time_in}"

class Departure(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    time_out = models.TimeField()
    time_out_date = models.DateField()

    def __str__(self):
        return f"{self.user.get_full_name()} departed from {self.place} on {self.time_out}"