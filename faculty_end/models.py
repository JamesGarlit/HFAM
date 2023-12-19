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

class FacultyAttendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='faculty_attendances')
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)

    def calculate_time_in_status(self):
        shift = self.get_shift()
        if shift:
            if shift.shift_start <= self.time_in <= shift.shift_end:
                return 'On Time'
            elif self.time_in > shift.shift_end:
                return 'Late'
        return 'No Schedule'

    def calculate_time_out_status(self):
        shift = self.get_shift()
        if shift and self.time_out:
            if self.time_out <= shift.shift_end:
                return 'Early'
        return 'No Schedule'

    def get_shift(self):
        try:
            return FacultyShift.objects.get(user=self.user, shift_day=self.date.strftime('%A'))
        except FacultyShift.DoesNotExist:
            return None