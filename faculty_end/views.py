# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LeaveApplication, TimeIn, TimeOut
from django.contrib.auth import authenticate, login, logout
from admin_end.models import FacultyShift
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
import requests

def is_faculty(user):
    return user.is_authenticated and not user.is_superuser

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def time_in(request, faculty_shift_id):
    faculty_shift = get_object_or_404(FacultyShift, pk=faculty_shift_id)
    user = request.user

    # Retrieve shift_start and shift_end for the faculty_shift
    shift_start = datetime.combine(datetime.today(), faculty_shift.shift_start)
    shift_end = datetime.combine(datetime.today(), faculty_shift.shift_end)

    # Check if the faculty member is absent for any schedule (30 minutes after shift_start) and no attendance record is present
    for schedule in user.faculty_shifts.all():
        schedule_start = datetime.combine(datetime.today(), schedule.shift_start)
        if datetime.now() > schedule_start + timedelta(minutes=30):
            # Use get() instead of get_or_create() to avoid creating a record with a null time_in
            try:
                time_in_record = TimeIn.objects.get(user=user, faculty_shift=schedule, date=datetime.now().date())
            except TimeIn.DoesNotExist:
                time_in_record = TimeIn.objects.create(
                    user=user,
                    faculty_shift=schedule,
                    date=datetime.now().date(),
                    status='Absent'
                )
                messages.warning(request, f'Automatically marked as Absent for {schedule} due to no time_in provided after 30 minutes.')

    if request.method == 'POST':
        location = request.POST.get('location')
        time_in_date = request.POST.get('time_in_date')
        time_in_input = request.POST.get('time_in')

        if time_in_input is not None:
            try:
                provided_time = datetime.strptime(time_in_input, '%H:%M').time()
            except ValueError:
                return render(request, 'faculty_end/time_in.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end, 'error_message': 'Invalid time format. Please use HH:MM.'})

            # Compare provided_time with faculty_shift.shift_start
            if provided_time == faculty_shift.shift_start:
                status = 'On Time'
            elif provided_time > faculty_shift.shift_start:
                status = 'Late'
            else:
                status = 'Early'

            time_in_record, created = TimeIn.objects.get_or_create(
                user=user,
                faculty_shift=faculty_shift,
                date=time_in_date,
                defaults={'time_in': provided_time, 'status': status, 'location': location}
            )
            messages.success(request, 'Time In Successful!')
            return redirect('attendance_record')

    return render(request, 'faculty_end/time_in.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end})

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def time_out(request, faculty_shift_id):
    faculty_shift = get_object_or_404(FacultyShift, pk=faculty_shift_id)
    user = request.user

    # Retrieve shift_start and shift_end for the faculty_shift
    shift_start = datetime.combine(datetime.today(), faculty_shift.shift_start)
    shift_end = datetime.combine(datetime.today(), faculty_shift.shift_end)

    # Check if the faculty member is absent for any schedule (30 minutes after shift_start) and no attendance record is present
    for schedule in user.faculty_shifts.all():
        schedule_end = datetime.combine(datetime.today(), schedule.shift_end)
        if datetime.now() > schedule_end + timedelta(minutes=30):
            # Use get() instead of get_or_create() to avoid creating a record with a null time_in
            try:
                time_out_record = TimeOut.objects.get(user=user, faculty_shift=schedule, date=datetime.now().date())
            except TimeOut.DoesNotExist:
                time_in_record = TimeOut.objects.create(
                    user=user,
                    faculty_shift=schedule,
                    date=datetime.now().date(),
                    status='Absent'
                )
                messages.warning(request, f'Automatically marked as Absent for {schedule} due to no time_in provided after 30 minutes.')

    if request.method == 'POST':
        location = request.POST.get('location')
        time_out_date = request.POST.get('time_out_date')
        time_out_input = request.POST.get('time_out')

        if time_out_input is not None:
            try:
                provided_time = datetime.strptime(time_out_input, '%H:%M').time()
            except ValueError:
                return render(request, 'faculty_end/time_out.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end, 'error_message': 'Invalid time format. Please use HH:MM.'})

            # Compare provided_time with faculty_shift.shift_end
            if provided_time == faculty_shift.shift_end:
                status = 'On Time'
            elif provided_time > faculty_shift.shift_end:
                status = 'Late'
            else:
                status = 'Early'

            time_out_record, created = TimeOut.objects.get_or_create(
                user=user,
                faculty_shift=faculty_shift,
                date=time_out_date,
                defaults={'time_out': provided_time, 'status': status, 'location': location}
            )
            messages.success(request, 'Time Out Successful!')
            return redirect('attendance_record')

    return render(request, 'faculty_end/time_out.html', {'faculty_shift': faculty_shift, 'shift_start': shift_start, 'shift_end': shift_end})


@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
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
@user_passes_test(is_faculty, login_url='error_400')
def leaveapp_list(request):
    leave_applications = LeaveApplication.objects.filter(user=request.user)
    return render(request, 'faculty_end/leaveapp_list.html', {'leave_applications': leave_applications})

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
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

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def faculty_logout(request):
    if request.user.is_authenticated:
        # Optional: Clear session data
        request.session.flush()

        # Logout the user
        logout(request)

        # Add a success message
        messages.success(request, 'Logout Successful!')
    else:
        # Add a warning message if the user is not authenticated
        messages.warning(request, 'You are not logged in.')

    # Redirect to the login page
    return redirect('faculty_login')

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def qrcode_generator(request):
    return render(request,'faculty_end/qrcode_generator.html')

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def account_settings(request):
    return render(request,'faculty_end/account_settings.html')

def error_400(request):
    return render(request,'faculty_end/error_400.html')

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
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

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')  
def notif(request):
    # Get the current user (faculty)
    faculty_user = request.user

    # Get the current day and time
    current_day = datetime.now().strftime('%A')  # Returns the full weekday name

    # Get all shifts for the current day
    faculty_shifts = FacultyShift.objects.filter(user=faculty_user, shift_day=current_day)

    # List to store messages for all shifts
    messages = []

    # Check each shift and create a message for it
    for shift in faculty_shifts:
        message = f"Your shift on {shift.get_schedule_display()} is scheduled today. Please mark your attendance."
        messages.append(message)

    # You can pass the list of messages to the template and render it
    return render(request, 'faculty_end/notif.html', {'messages': messages})

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_current_password = request.POST.get('confirm_current_password')

        # Check if the current password is correct
        if request.user.check_password(current_password):
            # Update the user's password
            request.user.set_password(new_password)
            request.user.save()

            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Your password was successfully updated!')
            return redirect('account_settings')
        else:
            messages.error(request, 'Current password is incorrect.')

    return render(request, 'faculty_end/account_settings.html')