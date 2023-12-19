# faculty_end/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LeaveApplication
from django.contrib.auth import authenticate, login, logout
from .forms import LeaveApplicationForm
from .models import FacultyAttendance
from admin_end.models import CustomUser
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
            return redirect('qrcode_scanner')
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
def qrcode_scanner(request):
    return render(request,'faculty_end/qrcode_scanner.html')
    
@login_required(login_url='faculty_login')
def qrcode_generator(request):
    return render(request,'faculty_end/qrcode_generator.html')

@login_required(login_url='faculty_login')
def save_attendance(request):
    if request.method == 'POST':
        # Retrieve data from the form
        user_id = request.user.id  # Use the current authenticated user's ID
        user_role = request.user.user_role  # Get the user role

        # Check if the authenticated user is a faculty
        if user_role == 'faculty':
            try:
                # Try to get the user with the specified ID and faculty role
                user = CustomUser.objects.get(id=user_id, user_role='faculty')
            except CustomUser.DoesNotExist:
                # Print an error message and return an HttpResponse
                print(f"Error: Faculty User with ID {user_id} does not exist.")
                return HttpResponse("Error: Faculty User does not exist.")

            location = request.POST.get('location')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            date = request.POST.get('date')
            time_in = request.POST.get('time_in')
            time_out = request.POST.get('time_out')

            # Create and save the attendance object
            attendance = FacultyAttendance(
                user=user,
                location=location,
                latitude=latitude,
                longitude=longitude,
                date=date,
                time_in=time_in,
                time_out=time_out,
            )
            attendance.save()

            return render(request, 'faculty_end/qrcode_scanner.html')
        else:
            # If the authenticated user is not a faculty, handle accordingly
            print("Error: User is not a faculty.")
            return HttpResponse("Error: User is not a faculty.")
    else:
        # Handle GET request or render the form
        return render(request, 'qrcode_scanner.html')
    
def attendance_record(request):
    # Retrieve attendance records for the authenticated faculty user
    attendance_records = FacultyAttendance.objects.filter(user=request.user)

    return render(request, 'faculty_end/attendance_record.html', {'attendance_records': attendance_records})