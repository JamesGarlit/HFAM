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
    coursesection = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    acadhead_created_at = models.DateTimeField(null=True, blank=True)
    checker_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    is_absent = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, null=True, blank= True)
    validation_comment = models.CharField(max_length=250, null=True, blank= True)
    justification_count = models.SmallIntegerField(default=0, null=True, blank=True)
    acadhead_is_responded = models.BooleanField(default=False)
    submitted_complaint = models.BooleanField(default=False)

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
    coursesection = models.CharField(max_length=50, blank=True, null=True)
    acadhead_created_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_absent = models.BooleanField(default=False)
    is_red_instruction = models.BooleanField(default=False)
    has_attachments = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False, null=True, blank= True)
    validation_comment = models.CharField(max_length=250, null=True, blank= True)
    justification_count = models.SmallIntegerField(default=0, null=True, blank=True)
    acadhead_is_responded = models.BooleanField(default=False)
    submitted_complaint = models.BooleanField(default=False)

class Complains(models.Model):
    onsite = models.OneToOneField(TimeIn, related_name='onsite_complains', on_delete=models.CASCADE, null=True, blank=True)
    complainant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    complained_date = models.DateTimeField(default=timezone.now)
    complains =  models.TextField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    validated_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    validated_by =  models.ForeignKey(CustomUser, related_name='validated_by' ,on_delete=models.CASCADE, null=True, blank=True)

class Evidence(models.Model):
    online = models.ForeignKey(Online, related_name='online_evidence', on_delete=models.CASCADE, null=True, blank=True)
    onsite = models.ForeignKey(TimeIn, related_name='onsite_evidence', on_delete=models.CASCADE, null=True, blank=True)
    complain = models.ForeignKey(Complains, related_name='complain_evidence', on_delete=models.CASCADE, null=True, blank=True)
    evidence = models.ImageField(upload_to='evidence_images/', blank=True, null=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(default=timezone.now)




