from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import cache_control
from django.contrib import messages
from .models import CustomUser, FacultyShift, AcademicYear, Semester, Approval, AttendanceNotification, FacultyAccount
from .forms import FacultyShiftForm
from faculty_end.models import LeaveApplication, TimeIn, TimeOut
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse

import requests

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='admin').exists()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def admin_notif(request):
    return render(request,'admin_end/admin_notif.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def admin_settings(request):
    return render(request,'admin_end/admin_settings.html')
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# USER FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_create(request):
    if request.method == 'POST':
        user_picture = request.FILES.get('user_picture')
        user_firstname = request.POST.get('user_firstname')
        user_lastname = request.POST.get('user_lastname')
        employment_status = request.POST.get('employment_status')
        user_role = request.POST.get('user_role')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = CustomUser(
            user_picture=user_picture,
            user_firstname=user_firstname,
            user_lastname=user_lastname,
            employment_status=employment_status,
            user_role=user_role,
            email=email,
            is_active=True,
            is_staff=True,
        )
        user.set_password(password)
        user.save()
        messages.success(request, 'User created successfully!')
        return redirect('user_list')
    else:
        # Render an empty form for GET requests
        return render(request, 'admin_end/user_create.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_update(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user_picture = request.FILES.get('user_picture')
        user_firstname = request.POST.get('user_firstname')
        user_lastname = request.POST.get('user_lastname')
        employment_status = request.POST.get('employment_status')
        user_role = request.POST.get('user_role')
        email = request.POST.get('email')
        new_password = request.POST.get('password')

        if new_password:
            # Update password only if a new one is provided
            user.set_password(new_password)
            user.save(update_fields=['password'])
            # Important: update_session_auth_hash to avoid log out after password change
            update_session_auth_hash(request, user)

        if user_picture:
            user.user_picture = user_picture
            user.user_firstname = user_firstname
            user.user_lastname = user_lastname
            user.employment_status = employment_status
            user.user_role = user_role

        # Check if the new role is 'superadmin' or 'admin' and update is_superuser accordingly
        if user_role in ['superadmin', 'admin']:
            user.is_superuser = True
        else:
            user.is_superuser = False

        user.email = email
        user.save(update_fields=['user_picture', 'user_firstname', 'user_lastname', 'employment_status', 'user_role', 'is_superuser', 'email'])

        messages.success(request, 'User information updated successfully!')
        return redirect('user_list')
    else:
        return render(request, 'admin_end/user_update.html', {'user': user})

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# SHIFT FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def faculty_members(request):
    api_url = 'https://pupqcfis-com.onrender.com/api/all/FISFaculty'

    response = requests.get(api_url)
    faculties_from_api = []

    if response.status_code == 200:
        api_data = response.json()
        faculty_account_ids = api_data.get('Faculties', {}).keys()

        for faculty_id in faculty_account_ids:
            faculty_info = api_data['Faculties'].get(faculty_id, {})
            faculty_data = {
                'FacultyId': faculty_id,
                'Rank': faculty_info.get('Rank', ''),
                'FirstName': faculty_info.get('FirstName', ''),
                'MiddleName': faculty_info.get('MiddleName', ''),
                'LastName': faculty_info.get('LastName', ''),
                'NameExtension': faculty_info.get('NameExtension', ''),
                'Email': faculty_info.get('Email', ''),
                'MobileNumber': faculty_info.get('MobileNumber', ''),
                'FacultyType': faculty_info.get('FacultyType', ''),
            }
            faculties_from_api.append(faculty_data)

    else:
        print("Failed to fetch data. Status code:", response.status_code)

    return render(request, 'admin_end/faculty_members.html', {'faculties_from_api': faculties_from_api} if faculties_from_api else {'error_message': 'Failed to fetch data from the API'})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)  
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login') 
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_end/user_list.html', {'users': users})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'admin_end/user_view.html', {'user': user})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_list(request):
    # Filter out deactivated faculty members
    faculty_list = CustomUser.objects.filter(user_role='faculty', is_active=True)
    
    # Get the schedule for each active faculty member
    faculty_schedule = []
    for faculty in faculty_list:
        shifts = FacultyShift.objects.filter(user=faculty)
        schedule_display = " / ".join(shift.get_schedule_display() for shift in shifts)
        faculty_schedule.append({
            'id': faculty.id,
            'name': faculty.get_full_name(),
            'employment_status': faculty.employment_status,
            'schedule_display': schedule_display,
        })

    return render(request, 'admin_end/shift_list.html', {'faculty_schedule': faculty_schedule})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_details(request, user_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')
    shifts = FacultyShift.objects.filter(user=faculty_user)
    return render(request, 'admin_end/shift_details.html', {'faculty_user': faculty_user, 'shifts': shifts})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_create(request, user_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')

    if request.method == 'POST':
        # Assuming you receive data for all models in the request.POST dictionary

        # Saving AcademicYear
        academic_year = AcademicYear.objects.create(
            user=faculty_user,
            year_start=request.POST.get('year_start'),
            year_end=request.POST.get('year_end')
        )

        # Saving Semester
        semester = Semester.objects.create(
            user=faculty_user,
            academic_year=academic_year,
            semester_name=request.POST.get('semester_name')
        )

        # Saving FacultyShift
        faculty_shift = FacultyShift.objects.create(
            user=faculty_user,
            academic_year=academic_year,
            semester=semester,
            shift_start=request.POST.get('shift_start'),
            shift_end=request.POST.get('shift_end'),
            shift_day=request.POST.get('shift_day')
        )

        # Assuming you have success messages set up
        messages.success(request, 'Shift Created Successfully!')

        return redirect('shift_details', user_id=user_id)
    else:
        # Assuming you have a template with the form fields
        return render(request, 'admin_end/shift_create.html', {'faculty_user': faculty_user})
# def shift_create(request, user_id):
#     faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')

#     if request.method == 'POST':
#         form = FacultyShiftForm(request.POST)
#         if form.is_valid():
#             shift = form.save(commit=False)
#             shift.user = faculty_user
#             shift.save()
#             messages.success(request, 'Shift Created Successfully!')
#             return redirect('shift_details', user_id=user_id)
#     else:
#         form = FacultyShiftForm()

#     return render(request, 'admin_end/shift_create.html', {'faculty_user': faculty_user, 'form': form})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_update(request, shift_id):
    shift = get_object_or_404(FacultyShift, id=shift_id)

    if request.method == 'POST':
        form = FacultyShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Update Successfully!')
            return redirect('shift_details', user_id=shift.user.id)
    else:
        form = FacultyShiftForm(instance=shift)

    return render(request, 'admin_end/shift_update.html', {'form': form, 'shift': shift})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_delete(request, shift_id):
    print(f"Received shift_id: {shift_id}")
    shift = get_object_or_404(FacultyShift, id=shift_id)
    
    if request.method == 'POST':
        shift.delete()
        return redirect('shift_details', user_id=shift.user.id)

    return render(request, 'admin_end/shift_delete.html', {'shift': shift})

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# LOGIN FUNCTION
def login_as(request):
    return render(request,'admin_end/login_as.html')

def admin_login(request):
    RECAPTCHA_SECRET_KEY = '6Lc_w1EpAAAAAPtl_6VlzrVSK8ufqIvpsG6MYwDE'  #reCAPTCHA secret key

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Check if email, password, and reCAPTCHA response are provided
        if not email or not password or not recaptcha_response:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'admin_end/admin_login.html')

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
            return render(request, 'admin_end/admin_login.html')

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None and user.user_role in ['admin', 'superadmin']:
            login(request, user)
            messages.success(request, 'Login Successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials or your credentials are not registered.')

    return render(request, 'admin_end/admin_login.html')

# LOGOUT FUNCTION
@login_required(login_url='admin_login')
def admin_logout(request):
    if request.user.is_authenticated:
        # Clear session data
        request.session.clear()

        # Logout the user
        logout(request)

        # Add a success message
        messages.success(request, 'Logout Successful!')
    else:
        # Add a warning message if the user is not authenticated
        messages.warning(request, 'You are not logged in.')

    # Redirect to the login page
    return redirect('admin_login')

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------

# DEACTIVATE USER FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'{user.user_firstname} {user.user_lastname} has been deactivated.')
    return redirect('user_list')

#  ACTIVATE USER FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'{user.user_firstname} {user.user_lastname} has been activated.')
    return redirect('user_list')
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------

# LEAVE APPLICATION LIST FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def leaveappreq_list(request):
    new_leave_applications = LeaveApplication.objects.filter(is_viewed=False)
    has_new_leave_applications = new_leave_applications.exists()

    # Update is_viewed to mark applications as viewed
    new_leave_applications.update(is_viewed=True)

    all_leave_applications = LeaveApplication.objects.all()

    return render(request, 'admin_end/leaveappreq_list.html', {
        'leave_applications': all_leave_applications,  # Display all applications in the table
        'has_new_leave_applications': has_new_leave_applications,
    })


# LEAVE APPLICATION FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def leaveappreq_view(request, leave_id):
    leave_application = LeaveApplication.objects.get(id=leave_id)
    return render(request, 'admin_end/leaveappreq_view.html', {'leave_application': leave_application})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def leaveappreq_decision(request, leave_id):
    leave_application = LeaveApplication.objects.get(id=leave_id)

    # Check if an associated Approval instance exists
    if not hasattr(leave_application, 'approval'):
        # If not, create a new Approval instance
        approval = Approval.objects.create(leave_application=leave_application)

    if request.method == 'POST':
        decision = request.POST.get('decision')
        comment = request.POST.get('comment')
        admin_user = get_user_model().objects.get(email=request.user.email)

        # Check if an associated Approval instance exists
        if not hasattr(leave_application, 'approval'):
            # If not, create a new Approval instance
            approval = Approval.objects.create(leave_application=leave_application)
        else:
            approval = leave_application.approval

        # Update the Approval instance
        approval.decision = decision
        approval.comment = comment
        approval.admin_user = admin_user
        approval.approval_datetime = timezone.now()  # Set the approval_datetime to the current date and time
        approval.save()

        # Notify faculty about the decision
        # (You may want to implement a notification mechanism)

        messages.success(request, f'Leave application {decision} successfully.')
        return redirect('leaveappreq_list')

    # Check if a decision has been made
    decision_made = hasattr(leave_application, 'approval') and leave_application.approval.decision is not None

    return render(request, 'admin_end/leaveappreq_view.html', {'leave_application': leave_application, 'decision_made': decision_made})

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# ATTENDANCE RECORD FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def faculty_attendance_record(request):
    all_faculty = CustomUser.objects.filter(user_role='faculty')

    # Get the selected year from the dropdown or use the current year
    selected_year = int(request.GET.get('selected_year', datetime.now().year))

    faculty_attendance_data = {}

    for faculty_member in all_faculty:
        time_in_records = TimeIn.objects.filter(user=faculty_member, date__year=selected_year)
        time_out_records = TimeOut.objects.filter(user=faculty_member, date__year=selected_year)

        for time_in_record in time_in_records:
            key = (time_in_record.date, faculty_member, time_in_record.faculty_shift.shift_start, time_in_record.faculty_shift.shift_end)

            if key not in faculty_attendance_data:
                faculty_attendance_data[key] = []

            faculty_attendance_data[key].append({
                'faculty_name': faculty_member.get_full_name(),
                'date': time_in_record.date,
                'shift_start': time_in_record.faculty_shift.shift_start,
                'shift_end': time_in_record.faculty_shift.shift_end,
                'time_in': time_in_record.time_in,
                'time_in_status': time_in_record.status,
                'time_in_location': time_in_record.location,
                'time_out': None,
                'time_out_status': None,
                'time_out_location': None,
            })

        for time_out_record in time_out_records:
            key = (time_out_record.date, faculty_member, time_out_record.faculty_shift.shift_start, time_out_record.faculty_shift.shift_end)

            if key in faculty_attendance_data:
                faculty_attendance_data[key][-1]['time_out'] = time_out_record.time_out
                faculty_attendance_data[key][-1]['time_out_status'] = time_out_record.status
                faculty_attendance_data[key][-1]['time_out_location'] = time_out_record.location

    context = {
        'faculty_attendance_data': [record for records in faculty_attendance_data.values() for record in records],
        'selected_year': selected_year,
        'all_years': range(datetime.now().year, 2020, -1),  # Change 2020 to the earliest year you want to include
    }

    return render(request, 'admin_end/faculty_attendance_record.html', context)

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# LATE NOTIFICATION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def attendance_notif(request):
    notifications = []

    # Retrieve TimeIn records
    time_in_records = TimeIn.objects.all()
    for time_in_record in time_in_records:
        notification = AttendanceNotification(
            user=time_in_record.user,
            date=time_in_record.date,
            time_in=time_in_record.time_in,
            status=time_in_record.status,
        )
        notifications.append(notification)

    # Retrieve TimeOut records
    time_out_records = TimeOut.objects.all()
    for time_out_record in time_out_records:
        notification = AttendanceNotification(
            user=time_out_record.user,
            date=time_out_record.date,
            time_out=time_out_record.time_out,
            status=time_out_record.status,
        )
        notifications.append(notification)

    context = {'notifications': notifications}
    return render(request, 'admin_end/attendance_notif.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def attendance_trends(request):
    # Your logic to fetch attendance data and prepare it for Highcharts
    # Example: Get attendance data for the last 30 days for users with the faculty role
    attendance_data = TimeIn.objects.filter(
        date__gte=datetime.date.today() - datetime.timedelta(days=30),
        user__user_role='faculty'
    )

    # Your logic to prepare data for Highcharts
    # Example: Create a list of dates and corresponding attendance counts
    dates = [entry.date for entry in attendance_data]
    
    # Check if either TimeIn or TimeOut is marked as absent
    attendance_counts = [
        entry.user.count()
        for entry in attendance_data
        if entry.status == 'Absent' or TimeOut.objects.filter(user=entry.user, date=entry.date, status='Absent').exists()
    ]

    return render(request, 'admin_end/dashboard.html', {'dates': dates, 'attendance_counts': attendance_counts})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def absenteeism_analysis(request):
    # Your logic to fetch absenteeism data and prepare it for Highcharts
    # Example: Get faculty members with frequent absences for users with the faculty role
    absenteeism_data = TimeIn.objects.filter(
        status='Absent',
        user__user_role='faculty'
    )

    # Your logic to prepare data for Highcharts
    # Example: Create a list of faculty names and corresponding absence counts
    faculty_names = [entry.user.username for entry in absenteeism_data]

    # Check if either TimeIn or TimeOut is marked as absent
    absence_counts = [
        faculty_names.count(faculty)
        for faculty in faculty_names
        if TimeOut.objects.filter(user__username=faculty, date__in=[entry.date for entry in absenteeism_data], status='Absent').exists()
    ]

    return render(request, 'admin_end/dashboard.html', {'faculty_names': faculty_names, 'absence_counts': absence_counts})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def dashboard(request):
    # Get current date
    current_date = timezone.now().date()

    # Query TimeIn and TimeOut models for the current day
    time_in_entries = TimeIn.objects.filter(date=current_date)
    time_out_entries = TimeOut.objects.filter(date=current_date)

    # Initialize an empty list to store faculty members who marked time
    faculty_members = []

    # Iterate through TimeIn entries and filter faculty members
    for time_in_entry in time_in_entries:
        if time_in_entry.user.user_role == 'faculty':
            faculty_member = time_in_entry.user
            if faculty_member not in faculty_members:
                faculty_members.append(faculty_member)

    # Iterate through TimeOut entries and filter faculty members
    for time_out_entry in time_out_entries:
        if time_out_entry.user.user_role == 'faculty':
            faculty_member = time_out_entry.user
            if faculty_member not in faculty_members:
                faculty_members.append(faculty_member)

    # Prepare data to pass to the template
    data = []
    for faculty_member in faculty_members:
        time_in_entry = TimeIn.objects.filter(user=faculty_member, date=current_date).first()
        time_out_entry = TimeOut.objects.filter(user=faculty_member, date=current_date).first()

        # Separate Time In entry
        if time_in_entry:
            data.append({
                'faculty_member': faculty_member,
                'user_picture': faculty_member.user_picture.url if faculty_member.user_picture else None,
                'time_in': time_in_entry.time_in,
                'time_in_status': time_in_entry.status,
                'time_in_location': time_in_entry.location,
                'time_out': None,
                'time_out_status': None,
                'time_out_location': None,
            })

        # Separate Time Out entry
        if time_out_entry:
            data.append({
                'faculty_member': faculty_member,
                'user_picture': faculty_member.user_picture.url if faculty_member.user_picture else None,
                'time_in': None,
                'time_in_status': None,
                'time_in_location': None,
                'time_out': time_out_entry.time_out,
                'time_out_status': time_out_entry.status,
                'time_out_location': time_out_entry.location,
            })

    # Render the template with the data
    return render(request, 'admin_end/dashboard.html', {'data': data, 'current_date': current_date})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def dashboard(request):
    # Assuming 'faculty' is the role you are considering for faculty members
    faculty_users = CustomUser.objects.filter(user_role='faculty')

    # Retrieve top 20 users with the most absent records (both in time in and time out)
    top_late_users = []
    for user in faculty_users:
        absences_count = TimeIn.objects.filter(user=user, status='Absent').count() + TimeOut.objects.filter(user=user, status='Absent').count()
        top_late_users.append({'user': user, 'absences_count': absences_count})

    # Sort the users based on the number of absences in descending order
    top_late_users.sort(key=lambda x: x['absences_count'], reverse=True)
    
    # Take only the top 20 users
    top_late_users = top_late_users[:15]

    context = {'top_late_users': top_late_users}
    return render(request, 'admin_end/dashboard.html', context)

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# SCHEDULE API FROM SCHEDULER
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def schedule_api(request):
    api_url = "https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpbnRlZ3JhdGlvbkBnbWFpbC5jb20iLCJ1c2VydHlwZSI6InN0YWZmIiwiZXhwIjoxNzA4NzA1Mjc5fQ.vBx_831N2vKXv913WShd4TmX_olT-XuHm7DNfTov2bI"

    headers = {
        'Authorization': f'Bearer {token}',
        # Add any other headers if required
    }

    try:
        response = requests.get(api_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()

            # Process the API response data
            schedule_data = []
            for entry in data['data']:
                schedule_info = {
                    'Faculty_Name': entry['facultyname'],
                    'Faculty_Status': entry['facultystatus'],
                    'Rank': entry['rank'],
                    'Course_Code': entry['course_code'],
                    'Course_Description': entry['course_description'],
                    'Units': entry['units'],
                    'Lecture': entry['lec'],
                    'Lab': entry['lab'],
                    'Class_Name': entry['classname'],
                    'Schedule': entry['schedule'],
                    'Room_Name': entry['roomname'],
                    'Created At': entry['created_at'],
                    'Created By': entry['created_by'],
                }

                schedule_data.append(schedule_info)

            return render(request, 'admin_end/schedule_api.html', {'schedule_data': schedule_data})
        else:
            # Handle other status codes appropriately
            return JsonResponse({'error': f'Request failed with status code {response.status_code}'}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that may occur during the request
        return JsonResponse({'error': f'Request failed: {str(e)}'}, status=500)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def create_faculty_account(request, faculty_id):
    try:
        existing_faculty_account = FacultyAccount.objects.get(faculty_id=faculty_id)
        messages.success(request, 'Faculty account already exists!')
        return redirect('faculty_members')
    except FacultyAccount.DoesNotExist:
        pass

    if request.method == 'POST':
        # Handle form submission
        # Extract form data from request.POST
        user_picture = request.POST.get('user_picture')
        user_firstname = request.POST.get('user_firstname')
        user_middlename = request.POST.get('user_middlename')
        user_lastname = request.POST.get('user_lastname')
        extension_name = request.POST.get('extension_name')
        employment_status = request.POST.get('employment_status')
        user_role = request.POST.get('user_role')
        email = request.POST.get('email')
        password = request.POST.get('password')  # Note: You may want to handle password securely (e.g., hashing)

        # Create CustomUser instance
        user = get_user_model().objects.create(
            user_picture=user_picture,
            user_firstname=user_firstname,
            user_middlename=user_middlename,
            user_lastname=user_lastname,
            extension_name=extension_name,
            employment_status=employment_status,
            user_role=user_role,
            email=email,
            is_active=True,
            is_staff=True,
        )

        user.set_password(password)
        user.save()

        # Create FacultyAccount instance
        faculty_account = FacultyAccount.objects.create(
            user=user,
            faculty_id=faculty_id,
        )
        messages.success(request, 'Account created successfully!')
        return redirect('faculty_members')

    # If not a POST request, retrieve data from the API
    api_url = 'https://pupqcfis-com.onrender.com/api/all/FISFaculty'
    response = requests.get(api_url)

    if response.status_code == 200:
        api_data = response.json()
        faculty_info = api_data.get('Faculties', {}).get(str(faculty_id), {})

        # Extract data from the API response and pass it to the template context
        context = {
            'faculty_id': faculty_id,
            'user_firstname': faculty_info.get('FirstName', ''),
            'user_middlename': faculty_info.get('MiddleName', ''),
            'user_lastname': faculty_info.get('LastName', ''),
            'extension_name': faculty_info.get('NameExtension', ''),
            'employment_status': faculty_info.get('FacultyType', ''),
            'email': faculty_info.get('Email', ''),
            # Do not include password for security reasons
        }

        return render(request, 'admin_end/create_faculty_account.html', context)
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        return HttpResponse("Failed to fetch data from the API.", status=response.status_code)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')  
def update_faculty_account(request, faculty_id):
    try:
        faculty_account = FacultyAccount.objects.get(faculty_id=faculty_id)
    except FacultyAccount.DoesNotExist:
        return HttpResponse("Faculty account not found.", status=404)

    if request.method == 'POST':
        # Handle form submission for updating faculty account
        # Extract form data from request.POST
        new_user_picture = request.FILES.get('user_picture')

        # Only update user_picture if a new file is provided
        if new_user_picture:
            faculty_account.user.user_picture = new_user_picture

        faculty_account.user.user_firstname = request.POST.get('user_firstname')
        faculty_account.user.user_middlename = request.POST.get('user_middlename')
        faculty_account.user.user_lastname = request.POST.get('user_lastname')
        faculty_account.user.extension_name = request.POST.get('extension_name')
        faculty_account.email = request.POST.get('email')
        # You may want to handle password update securely (e.g., hashing)
        faculty_account.password = request.POST.get('password')

        # Save the updated faculty account
        faculty_account.user.save()  # Save the associated user instance
        faculty_account.save()

        # Redirect or display a success message as needed
        messages.success(request, 'Faculty account updated successfully!')
        return redirect('faculty_members')

    # If not a POST request, retrieve data from the API or database
    api_url = 'https://pupqcfis-com.onrender.com/api/all/FISFaculty'
    response = requests.get(api_url)

    if response.status_code == 200:
        api_data = response.json()
        faculty_info = api_data.get('Faculties', {}).get(str(faculty_id), {})

        # Extract data from the API response and pass it to the template context
        context = {
            'faculty_id': faculty_id,
            'user_firstname': faculty_info.get('FirstName', ''),
            'user_middlename': faculty_info.get('MiddleName', ''),
            'user_lastname': faculty_info.get('LastName', ''),
            'extension_name': faculty_info.get('NameExtension', ''),
            'employment_status': faculty_info.get('FacultyType', ''),
            'email': faculty_info.get('Email', ''),
            # Do not include password for security reasons
        }

        return render(request, 'admin_end/update_faculty_account.html', context)
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        return HttpResponse("Failed to fetch data from the API.", status=response.status_code)