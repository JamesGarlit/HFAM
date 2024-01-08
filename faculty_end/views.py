# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LeaveApplication, TimeIn, TimeOut
from django.contrib.auth import authenticate, login, logout
from .forms import LeaveApplicationForm
from admin_end.models import FacultyShift
from datetime import datetime, time
from django.http import HttpResponse

@login_required(login_url='faculty_login')
def leaveapp_create(request):
    form = LeaveApplicationForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form.instance.user = request.user
        form.save()
        messages.success(request, 'Leave application submitted successfully.')
        return redirect('leaveapp_list')

    return render(request, 'faculty_end/leaveapp_create.html', {'form': form})

@login_required(login_url='faculty_login')
def leaveapp_list(request):
    leave_applications = LeaveApplication.objects.filter(user=request.user)
    return render(request, 'faculty_end/leaveapp_list.html', {'leave_applications': leave_applications})

@login_required(login_url='faculty_login')
def leaveapp_view(request, leave_id):
    leave_application = LeaveApplication.objects.get(id=leave_id)
    return render(request, 'faculty_end/leaveapp_view.html', {'leave_application': leave_application})

def faculty_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None and user.user_role == 'faculty':
            login(request, user)
            messages.success(request, 'Logged In Successful!')
            return redirect('qrcode_generator')
        else:
            messages.error(request, 'Incorrect credentials. Please try again.')
            return render(request, 'faculty_end/faculty_login.html')

    return render(request, 'faculty_end/faculty_login.html')

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

    if request.method == 'POST':
        location = request.POST.get('location')
        time_in_date = request.POST.get('time_in_date')
        time_in_input = request.POST.get('time_in')

        if time_in_input is not None:
            try:
                provided_time = datetime.strptime(time_in_input, '%H:%M').time()
            except ValueError:
                return HttpResponse('Invalid time format. Please use HH:MM.')

            status = get_time_status(provided_time, faculty_shift.shift_start)

            time_in_record, created = TimeIn.objects.get_or_create(
                user=user,
                faculty_shift=faculty_shift,
                date=time_in_date,
                defaults={'time_in': provided_time, 'status': status, 'location': location}
            )
            messages.success(request, 'Time In Successful!')
            return redirect('attendance_record')

    return render(request, 'faculty_end/time_in.html', {'faculty_shift': faculty_shift})

def time_out(request, faculty_shift_id):
    faculty_shift = get_object_or_404(FacultyShift, pk=faculty_shift_id)
    user = request.user

    if request.method == 'POST':
        location = request.POST.get('location')
        time_out_date = request.POST.get('date')
        time_out_input = request.POST.get('time_out')

        if time_out_input is not None:
            try:
                provided_time = datetime.strptime(time_out_input, '%H:%M').time()
            except ValueError:
                return HttpResponse('Invalid time format. Please use HH:MM.')

            status = get_time_status(provided_time, faculty_shift.shift_end)

            # Explicitly set the date field when creating a new TimeOut record
            time_out_record, created = TimeOut.objects.get_or_create(
                user=user,
                faculty_shift=faculty_shift,
                date=time_out_date,
                defaults={'time_out': provided_time, 'status': status, 'location': location}
            )

            messages.success(request, 'Time Out Successful!')
            return redirect('attendance_record')

    return render(request, 'faculty_end/time_out.html', {'faculty_shift': faculty_shift})

def get_time_status(current_time, target_time):
    # Compare the current time with the target time and determine the status
    if current_time == target_time:
        return 'On Time'
    elif current_time > target_time:
        return 'Late'
    else:
        return 'Early'
