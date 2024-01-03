# faculty_end/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LeaveApplication, Place, Arrival, Departure
from django.contrib.auth import authenticate, login, logout
from .forms import LeaveApplicationForm
from django.utils import timezone

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
            return redirect('attendance_record')
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
def time_in(request):
    return render(request,'faculty_end/time_in.html')

@login_required(login_url='faculty_login')
def attendance_record(request):
    # Retrieve the current user's Arrival and Departure records
    user_arrivals = Arrival.objects.filter(user=request.user)
    user_departures = Departure.objects.filter(user=request.user)

    # Combine user Arrival and Departure records
    user_records = list(user_arrivals) + list(user_departures)

    # Sort user records by date and time in descending order (from latest to oldest)
    user_records = sorted(user_records, key=lambda x: (x.time_in_date if hasattr(x, 'time_in_date') else x.time_out_date,
                                                       x.time_in if hasattr(x, 'time_in') else x.time_out),
                          reverse=True)

    return render(request, 'faculty_end/attendance_record.html', {'records': user_records})

def time_in(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        time_in_date = request.POST.get('time_in_date')
        time_in_time = request.POST.get('time_in')

        # Assuming you have a user associated with the request, you can get it like this
        user = request.user

        # Create or get the Place object
        place, created = Place.objects.get_or_create(
            location=location,
            latitude=latitude,
            longitude=longitude
        )

        # Create the Arrival object with only the time component
        arrival = Arrival.objects.create(
            user=user,
            place=place,
            time_in=timezone.datetime.strptime(time_in_time, "%H:%M").time(),
            time_in_date=time_in_date
        )
        messages.success(request, 'Time in successfully!')
        # You can do additional processing or redirect to another page if needed
        return redirect('attendance_record')

    return render(request, 'faculty_end/time_in.html')

def time_out(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        time_out_date = request.POST.get('time_in_date')
        time_out_time = request.POST.get('time_out')

        # Assuming you have a user associated with the request, you can get it like this
        user = request.user

        # Create or get the Place object
        place, created = Place.objects.get_or_create(
            location=location,
            latitude=latitude,
            longitude=longitude
        )

        # Create the Departure object with only the time component
        departure = Departure.objects.create(
            user=user,
            place=place,
            time_out=timezone.datetime.strptime(time_out_time, "%H:%M").time(),
            time_out_date=time_out_date
        )
        messages.success(request, 'Time out successfully!')
        # You can do additional processing or redirect to another page if needed
        return redirect('attendance_record')

    return render(request, 'faculty_end/time_out.html')

