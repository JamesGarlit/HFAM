from rest_framework import serializers
from faculty_end.models import LeaveApplication

class LeaveApplicationSerializers(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ['id', 'user', 'leave_start_time', 'leave_start_date', 'leave_end_time', 'leave_end_date', 'leave_type', 'leave_reason', 'leave_supporting_docs']