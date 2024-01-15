# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LeaveApplication, TimeIn, TimeOut
from django.contrib.auth import authenticate, login, logout
from admin_end.models import FacultyShift
from datetime import datetime
from django.utils import timezone
import requests

@login_required(login_url='faculty_login')
def leaveapp_create(request):
    if request.method == 'POST':
        # Extract data from the request
        user = request.user  # Assuming the user is authenticated
        leave_start_date = request.POST.get('leave_start_date')
        leave_start_time = request.POST.get('leave_start_time')
        leave_end_date = request.POST.get('leave_end_date')
        leave_end_time = request.POST.get('leave_end_time')
        leave_type = request.POST.get('leave_type')
        leave_reason = request.POST.get('leave_reason')
        leave_supporting_docs = request.FILES.get('leave_supporting_docs') if 'leave_supporting_docs' in request.FILES else None

        # Combine date and time fields to create datetime objects
        leave_start_datetime_str = f'{leave_start_date} {leave_start_time}'
        leave_end_datetime_str = f'{leave_end_date} {leave_end_time}'

        # Try to parse datetime using the 12-hour format first
        try:
            leave_start_datetime = datetime.strptime(leave_start_datetime_str, '%Y-%m-%d %I:%M %p')
            leave_end_datetime = datetime.strptime(leave_end_datetime_str, '%Y-%m-%d %I:%M %p')
        except ValueError:
            # If parsing with 12-hour format fails, try 24-hour format
            leave_start_datetime = datetime.strptime(leave_start_datetime_str, '%Y-%m-%d %H:%M')
            leave_end_datetime = datetime.strptime(leave_end_datetime_str, '%Y-%m-%d %H:%M')

        # Create LeaveApplication instance
        leave_application = LeaveApplication.objects.create(
            user=user,
            leave_start_date=leave_start_datetime.date(),
            leave_start_time=leave_start_datetime.time(),
            leave_end_date=leave_end_datetime.date(),
            leave_end_time=leave_end_datetime.time(),
            leave_type=leave_type,
            leave_reason=leave_reason,
            leave_supporting_docs=leave_supporting_docs,
        )
        messages.success(request, 'Leave application submitted successfully!')
        # Redirect to a success page or display a success message
        return redirect('leaveapp_list')

    # If the request method is GET, render the template with a form for creating a leave application
    return render(request, 'faculty_end/leaveapp_create.html')

@login_required(login_url='faculty_login')
def leaveapp_list(request):
    leave_applications = LeaveApplication.objects.filter(user=request.user)
    return render(request, 'faculty_end/leaveapp_list.html', {'leave_applications': leave_applications})

@login_required(login_url='faculty_login')
def leaveapp_view(request, leave_id):
    leave_application = LeaveApplication.objects.get(id=leave_id)
    return render(request, 'faculty_end/leaveapp_view.html', {'leave_application': leave_application})

def faculty_login(request):
    RECAPTCHA_SECRET_KEY = '6Lc_w1EpAAAAAPtl_6VlzrVSK8ufqIvpsG6MYwDE'  # Replace with your actual reCAPTCHA secret key

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Check if email, password, and reCAPTCHA response are provided
        if not email or not password or not recaptcha_response:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'faculty_end/faculty_login.html')

        # Verify reCAPTCHA
        url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }

        response = requests.post(url, data=data)
        result = response.json()

        if not result.get('success', False):
            messages.error(request, 'reCAPTCHA verification failed. Please try again.')
            return render(request, 'faculty_end/faculty_login.html')

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None and user.user_role == 'faculty':
            login(request, user)
            messages.success(request, 'Logged In Successfully!')
            return redirect('attendance_record')
        else:
            messages.error(request, 'Incorrect credentials or user is not a faculty member.')
            return render(request, 'faculty_end/faculty_login.html')

    return render(request, 'faculty_end/faculty_login.html')
# def faculty_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email=email, password=password)

#         if user is not None and user.user_role == 'faculty':
#             login(request, user)
#             messages.success(request, 'Logged In Successful!')
#             return redirect('attendance_record')
#         else:
#             messages.error(request, 'Incorrect credentials. Please try again.')
#             return render(request, 'faculty_end/faculty_login.html')

#     return render(request, 'faculty_end/faculty_login.html')

@login_required(login_url='faculty_login')
def faculty_logout(request):
    logout(request)
    messages.success(request, 'Logout Successful!')
    return redirect('faculty_login')
    
@login_required(login_url='faculty_login')
def qrcode_generator(request):
    return render(request,'faculty_end/qrcode_generator.html')

def attendance_record(request):
    # Get the current user
    user = request.user

    # Get the current date
    current_date = datetime.now().date()

    # Get the faculty shifts for the current date and the current user
    faculty_shifts = FacultyShift.objects.filter(user=user, shift_day=current_date.strftime('%A'))

    # Retrieve TimeIn and TimeOut records for each faculty shift
    for faculty_shift in faculty_shifts:
        time_in_record = TimeIn.objects.filter(user=user, faculty_shift=faculty_shift, date=current_date).first()
        time_out_record = TimeOut.objects.filter(user=user, faculty_shift=faculty_shift, date=current_date).first()

        if time_in_record:
            faculty_shift.time_in = time_in_record.time_in
            faculty_shift.time_in_status = time_in_record.status
            faculty_shift.time_in_location = time_in_record.location

        if time_out_record:
            faculty_shift.time_out = time_out_record.time_out
            faculty_shift.time_out_status = time_out_record.status
            faculty_shift.time_out_location = time_out_record.location

    # Render the template with the faculty shifts
    return render(request, 'faculty_end/attendance_record.html', {'faculty_shifts': faculty_shifts, 'current_date': current_date})

def time_in(request, faculty_shift_id):
    faculty_shift = get_object_or_404(FacultyShift, pk=faculty_shift_id)
    user = request.user

    # Retrieve shift_start and shift_end for the faculty_shift
    shift_start = faculty_shift.shift_start
    shift_end = faculty_shift.shift_end

    if request.method == 'POST':
        location = request.POST.get('location')
        time_in_date = request.POST.get('time_in_date')
        time_in_input = request.POST.get('time_in')

        if time_in_input is not None:
            try:
                provided_time = datetime.strptime(time_in_input, '%H:%M').time()
            except ValueError:
                return render(request, 'faculty_end/time_in.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end, 'error_message': 'Invalid time format. Please use HH:MM.'})

            status = get_time_status(provided_time, faculty_shift.shift_start)

            time_in_record, created = TimeIn.objects.get_or_create(
                user=user,
                faculty_shift=faculty_shift,
                date=time_in_date,
                defaults={'time_in': provided_time, 'status': status, 'location': location}
            )
            messages.success(request, 'Time In Successful!')
            return redirect('attendance_record')

    return render(request, 'faculty_end/time_in.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end})

def time_out(request, faculty_shift_id):
    faculty_shift = get_object_or_404(FacultyShift, pk=faculty_shift_id)
    user = request.user

    # Retrieve shift_start and shift_end for the faculty_shift
    shift_start = faculty_shift.shift_start
    shift_end = faculty_shift.shift_end

    if request.method == 'POST':
        location = request.POST.get('location')
        time_out_date = request.POST.get('time_out_date')
        time_out_input = request.POST.get('time_out')

        if time_out_input is not None:
            try:
                provided_time = datetime.strptime(time_out_input, '%H:%M').time()
            except ValueError:
                return render(request, 'faculty_end/time_out.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end, 'error_message': 'Invalid time format. Please use HH:MM.'})

            status = get_time_status(provided_time, faculty_shift.shift_end)

            time_out_record, created = TimeOut.objects.get_or_create(
                user=user,
                faculty_shift=faculty_shift,
                date=time_out_date,
                defaults={'time_out': provided_time, 'status': status, 'location': location}
            )
            messages.success(request, 'Time Out Successful!')
            return redirect('attendance_record')

    return render(request, 'faculty_end/time_out.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end})

def get_time_status(current_time, target_time):
    # Compare the current time with the target time and determine the status
    if current_time == target_time:
        return 'On Time'
    elif current_time > target_time:
        return 'Late'
    else:
        return 'Early'
    
def notify_faculty(request):
    # Get the current user (faculty)
    current_user = request.user

    # Get the faculty's shift for the current day
    current_day = timezone.now().strftime('%A')
    faculty_shift = FacultyShift.objects.filter(user=current_user, shift_day=current_day).first()

    if faculty_shift:
        # Calculate the time difference between now and the shift start time
        time_difference = faculty_shift.shift_start - timezone.now().time()

        # Check if it's less than or equal to 2 minutes before the shift start
        if 0 <= time_difference.seconds <= 2 * 60:
            # Send a notification
            messages.info(request, 'Your shift will start in 2 minutes.')
