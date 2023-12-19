# faculty_end/forms.py
from django import forms
from .models import LeaveApplication

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_start_date', 'leave_end_date', 'leave_type', 'leave_reason', 'leave_supporting_docs']
        widgets = {
            'leave_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'leave_reason': forms.Textarea(attrs={'class': 'form-control'}),
            'leave_supporting_docs': forms.FileInput(attrs={'class': 'form-control'}),
        }

# # faculty_end/forms.py
# from django import forms
# from .models import AttendanceRecord

# class AttendanceRecordForm(forms.ModelForm):
#     class Meta:
#         model = AttendanceRecord
#         fields = ['time_in', 'timein_status', 'time_out', 'timeout_status', 'location', 'longitude', 'latitude', 'date']
