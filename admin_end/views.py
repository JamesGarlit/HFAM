from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import cache_control
from django.contrib import messages
from .models import CustomUser, FacultyShift, AcademicYear, Semester, AttendanceNotification, FacultyAccount, LeaveApplicationAction
from faculty_end.models import LeaveApplication, TimeIn, Online, TimeOut
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import dateutil.parser
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='admin').exists()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def admin_notif(request):
    return render(request,'admin_end/admin_notif.html')

def dashboard(request):
    return render(request,'admin_end/dashboard.html')

def top_faculty_present_status(request):
    return render(request, 'admin_end/dashboard.html')

def get_top_faculty_present_status_data(request):
    # Get the top 20 faculty users
    faculty_users = CustomUser.objects.filter(user_role='faculty')
    
    # Aggregate present status counts
    present_status_counts = (
        TimeIn.objects.filter(user__in=faculty_users, status='Present')
        .values('user')
        .annotate(present_count=Count('status'))
        .order_by('-present_count')[:20]
    )

    # Prepare data for Highcharts
    chart_data = [{
        'name': CustomUser.objects.get(id=entry['user']).username,
        'y': entry['present_count']
    } for entry in present_status_counts]

    return JsonResponse(chart_data, safe=False)

def generate_qr(request):
    return render(request,'admin_end/generate_qr.html')

def onlineqrcode(request):
    return render(request,'admin_end/onlineqrcode.html')

def present_users_chart(request):
    present_users_timein = TimeIn.objects.filter(status="Present", user__user_role="faculty").values('user__email').annotate(count=Count('user'))
    present_users_online = Online.objects.filter(status="Present", user__user_role="faculty").values('user__email').annotate(count=Count('user'))
    
    # Merge the results from both queries
    present_users = present_users_timein.union(present_users_online)
    
    data = [{'name': user['user__email'], 'y': user['count']} for user in present_users]
    
    return JsonResponse(data, safe=False)

def absent_users_chart(request):
    absent_users_timein = TimeIn.objects.filter(status="Absent", user__user_role="faculty").values('user__email').annotate(count=Count('user'))
    absent_users_online = Online.objects.filter(status="Absent", user__user_role="faculty").values('user__email').annotate(count=Count('user'))
    
    # Merge the results from both queries
    absent_users = absent_users_timein.union(absent_users_online)
    
    data = [{'name': user['user__email'], 'y': user['count']} for user in absent_users]
    
    return JsonResponse(data, safe=False)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)

@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def admin_settings(request):
    return render(request,'admin_end/admin_settings.html')
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# USER FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
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
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def user_update(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user_picture = request.FILES.get('user_picture')
        user_firstname = request.POST.get('user_firstname')
        user_middlename = request.POST.get('user_middlename')
        user_lastname = request.POST.get('user_lastname')
        extension_name = request.POST.get('extension_name')
        employment_status = request.POST.get('employment_status')
        user_role = request.POST.get('user_role')
        email = request.POST.get('email')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if new_password and new_password == confirm_password:
            # Update password only if a new one is provided and matches the confirm password
            user.set_password(new_password)
            user.save(update_fields=['password'])
            # Important: update_session_auth_hash to avoid log out after password change
            update_session_auth_hash(request, user)

        if user_picture:
            user.user_picture = user_picture
        user.user_firstname = user_firstname
        user.user_middlename = user_middlename
        user.user_lastname = user_lastname
        user.extension_name = extension_name
        user.employment_status = employment_status
        user.user_role = user_role

        # Check if the new role is 'superadmin' or 'admin' and update is_superuser accordingly
        if user_role in ['superadmin', 'admin']:
            user.is_superuser = True
        else:
            user.is_superuser = False

        user.email = email
        user.save()

        messages.success(request, 'User information updated successfully!')
        return redirect('user_list')
    else:
        return render(request, 'admin_end/user_update.html', {'user': user})

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# SHIFT FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def faculty_members(request):
    api_url = 'https://pupqcfis-com.onrender.com/api/all/FISFaculty'
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJrZXkiOiI1NGY0NzRmMTAxYTc0NWRhYmRiODU1M2I4YzYzMzliMSJ9.hNjCSVI3bsaivK3JlAOqGBlrMkvZxUptUxSqCCD5STs'

    headers = {
        'Authorization': 'API-Key',
        'token': token,
    }

    response = requests.get(api_url, headers=headers)
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
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as') 
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_end/user_list.html', {'users': users})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def user_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'admin_end/user_view.html', {'user': user})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def shift_list(request):
    # Fetch all users with role 'faculty' along with their shifts
    faculty_shifts = FacultyShift.objects.select_related('user', 'academic_year', 'semester').filter(user__user_role='faculty')

    # Initialize an empty dictionary to store the data for each faculty member
    faculty_shift_data = {}

    # Iterate over each faculty member's shifts
    for shift in faculty_shifts:
        # If the faculty member is not in the dictionary, add them with their shifts
        if shift.user not in faculty_shift_data:
            faculty_shift_data[shift.user] = {
                'user': shift.user,
                'academic_year': shift.academic_year if shift.academic_year else 'No Data',
                'semester': shift.semester if shift.semester else 'No Data',
                'shifts': f"{shift.shift_day} {shift.shift_start.strftime('%I:%M %p')} - {shift.shift_end.strftime('%I:%M %p')}"
            }
        # If the faculty member is already in the dictionary, append the shift details
        else:
            faculty_shift_data[shift.user]['shifts'] += f" / {shift.shift_day} {shift.shift_start.strftime('%I:%M %p')} - {shift.shift_end.strftime('%I:%M %p')}"

    # Check for faculty members without shifts and add them to the dictionary with 'No Data'
    all_faculty_members = CustomUser.objects.filter(user_role='faculty')
    for faculty_member in all_faculty_members:
        if faculty_member not in faculty_shift_data:
            faculty_shift_data[faculty_member] = {
                'user': faculty_member,
                'academic_year': 'No Data',
                'semester': 'No Data',
                'shifts': 'No shift yet'
            }

    # Convert the dictionary values to a list for template rendering
    faculty_shift_data_list = list(faculty_shift_data.values())

    # Pass the data to the template for rendering
    return render(request, 'admin_end/shift_list.html', {'faculty_shift_data': faculty_shift_data_list})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def shift_details(request, user_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')
    shifts = FacultyShift.objects.filter(user=faculty_user)
    return render(request, 'admin_end/shift_details.html', {'faculty_user': faculty_user, 'shifts': shifts})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
@transaction.atomic
def shift_create(request, user_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')

    if request.method == 'POST':
        academic_year = AcademicYear.objects.create(
            user=faculty_user,
            year_start=request.POST.get('year_start'),
            year_end=request.POST.get('year_end')
        )

        semester = Semester.objects.create(
            user=faculty_user,
            academic_year=academic_year,
            semester_name=request.POST.get('semester_name')
        )

        shift_start = request.POST.getlist('shift_start[]')
        shift_end = request.POST.getlist('shift_end[]')
        shift_day = request.POST.getlist('shift_day[]')

        # Create FacultyShift objects for each shift
        for start, end, day in zip(shift_start, shift_end, shift_day):
            FacultyShift.objects.create(
                user=faculty_user,
                academic_year=academic_year,
                semester=semester,
                shift_start=start,
                shift_end=end,
                shift_day=day
            )

        messages.success(request, 'Shifts Created Successfully!')
        return redirect('shift_details', user_id=user_id)
    else:
        return render(request, 'admin_end/shift_create.html', {'faculty_user': faculty_user})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def shift_update(request, user_id, shift_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')
    shift = get_object_or_404(FacultyShift, id=shift_id)
    academic_years = AcademicYear.objects.all()

    if request.method == 'POST':
        # Assuming you have form fields for updating shift details directly in the HTML
        shift.shift_start = request.POST.get('shift_start')
        shift.shift_end = request.POST.get('shift_end')
        shift.shift_day = request.POST.get('shift_day')
        shift.save()

        # Update associated AcademicYear and Semester
        academic_year = shift.academic_year
        academic_year.year_start = request.POST.get('year_start')
        academic_year.year_end = request.POST.get('year_end')
        academic_year.save()

        semester = shift.semester
        semester.semester_name = request.POST.get('semester_name')
        semester.save()

        messages.success(request, 'Shift and Associated Details Updated Successfully!')
        return redirect('shift_details', user_id=user_id)
    else:
        return render(request, 'admin_end/shift_update.html', {'shift': shift, 'faculty_user': faculty_user, 'academic_years': academic_years})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def shift_delete(request, shift_id):
    print(f"Received shift_id: {shift_id}")
    shift = get_object_or_404(FacultyShift, id=shift_id)
    
    if request.method == 'POST':
        shift.delete()
        return redirect('shift_details', user_id=shift.user.id)

    return render(request, 'admin_end/shift_delete.html', {'shift': shift})

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# # LOGIN FUNCTION
def login_as(request):
    RECAPTCHA_SECRET_KEY = '6Lc_w1EpAAAAAPtl_6VlzrVSK8ufqIvpsG6MYwDE'  # reCAPTCHA secret key

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Check if email, password, and reCAPTCHA response are provided
        if not email or not password or not recaptcha_response:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'admin_end/login_as.html')

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
            return render(request, 'admin_end/login_as.html')

        # Check if user has been banned
        banned_until = request.session.get('banned_until')
        if banned_until:
            banned_until = dateutil.parser.parse(banned_until)
            if banned_until > timezone.now():
                time_left = (banned_until - timezone.now()).total_seconds() // 60
                messages.error(request, f'You have been banned. Try again after {time_left} minutes.')
                return render(request, 'admin_end/login_as.html')


        # Attempt to authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Reset login attempts if successful
            request.session.pop('login_attempts', None)

            # Redirect based on user role
            if user.user_role == 'admin' or user.user_role == 'superadmin':
                login(request, user)
                messages.success(request, 'Admin logged in successful.')
                return redirect('dashboard')  # Redirect to admin dashboard
            elif user.user_role == 'faculty':
                login(request, user)
                messages.success(request, 'Faculty logged in successful.')
                return redirect('log_time_in')  # Redirect to faculty home page
            else:
                messages.error(request, 'Invalid user role.')
        else:
            # Increase login attempts count
            login_attempts = request.session.get('login_attempts', 0) + 1
            request.session['login_attempts'] = login_attempts

            # Check if login attempts exceed limit
            if login_attempts >= 3:
                # Ban the user for 3 minutes
                banned_until = timezone.now() + timedelta(minutes=3)
                request.session['banned_until'] = str(banned_until)  # Convert to string
                messages.error(request, 'You have exceeded the login attempts limit. Please try again later.')
            else:
                messages.error(request, 'Invalid credentials.')

    return render(request, 'admin_end/login_as.html')

# LOGOUT FUNCTION
@login_required(login_url='login_as')
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
    return redirect('login_as')

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------

# DEACTIVATE USER FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'{user.user_firstname} {user.user_lastname} has been deactivated.')
    return redirect('user_list')

#  ACTIVATE USER FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
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
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
# def leaveappreq_list(request):
#     faculty_leave_apps = LeaveApplication.objects.all()  # Get all leave applications
#     return render(request, 'admin_end/leaveappreq_list.html', {'faculty_leave_apps': faculty_leave_apps})

def leaveappreq_list(request):
    # Fetch all leave applications
    all_leave_apps = LeaveApplication.objects.all()

    # Filter leave applications based on status if a status is selected
    status_filter = request.GET.get('status')
    if status_filter == 'Pending':
        all_leave_apps = all_leave_apps.filter(Q(leaveapplicationaction__status=status_filter) | Q(leaveapplicationaction__status__isnull=True))
    elif status_filter:
        all_leave_apps = all_leave_apps.filter(leaveapplicationaction__status=status_filter)

    return render(request, 'admin_end/leaveappreq_list.html', {'all_leave_apps': all_leave_apps})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def approval(request, leave_app_id):
    leave_app = LeaveApplication.objects.get(pk=leave_app_id)
    if request.method == 'POST':
        comment = request.POST.get('comment')
        action = request.POST.get('action')

        # Check if the leave application has already been approved or rejected
        if LeaveApplicationAction.objects.filter(leave_application=leave_app).exists():
            messages.error(request, 'This leave application has already been processed.')

        # Get the user ID of the faculty member who filled the leave application
        faculty_user_id = leave_app.user_id

        # Create a LeaveApplicationAction instance for the faculty member and leave application
        leave_action = LeaveApplicationAction.objects.create(
            user_id=faculty_user_id,
            leave_application=leave_app,
            status='Accepted' if action == 'accept' else 'Rejected',
            comment=comment
        )
        leave_action.save()

        # Redirect to the leave applications page after processing
        return redirect('leaveappreq_list')

    return render(request, 'admin_end/approval.html', {'leave_app': leave_app})
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# ATTENDANCE RECORD FUNCTION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')

def faculty_attendance_records(request):
    # Fetch all faculty users with the faculty role
    faculty_users = CustomUser.objects.filter(user_role='faculty')

    # Initialize an empty dictionary to store attendance records for each faculty member
    faculty_attendance = {}

    # Iterate over faculty users
    for faculty_user in faculty_users:
        # Fetch TimeIn and TimeOut records for the current faculty user
        time_in_records = TimeIn.objects.filter(user=faculty_user)
        time_out_records = TimeOut.objects.filter(user=faculty_user)


        print(time_in_records)

        print(time_out_records)

        # Combine TimeIn and TimeOut records for display
        attendance_records = []
        for record in time_in_records:
            attendance_records.append({
                'user': faculty_user.get_full_name(),
                'date': record.date,
                # 'location': record.location,
                'time': record.time_in,
                'status': record.status,
                'timeintimeout': 'Time In',  # Indicates Time In record
            })
            print('lakas', record)
            
        for time_out_record in time_out_records:
            attendance_records.append({
                'user': faculty_user.get_full_name(),
                'date': time_out_record.date,
                'location': time_out_record.location,
                'time': time_out_record.time_out,
                'status': time_out_record.status,
                'timeintimeout': 'Time Out',  # Indicates Time Out record
            })

        # Sort attendance records based on date and time
        sorted_records = sorted(attendance_records, key=lambda x: (x['date'], x['time']))

        # Store the sorted attendance records for the current faculty user in the dictionary
        faculty_attendance[faculty_user.get_full_name()] = sorted_records

    # Pass the attendance records for each faculty member to the template for rendering
    context = {
        'faculty_attendance': faculty_attendance,
    }
    print(faculty_attendance)
    return render(request, 'admin_end/faculty_attendance_records.html', context)



# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# LATE NOTIFICATION
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
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

    # Paginate notifications
    paginator = Paginator(notifications, 10)  # 10 items per page
    page_number = request.GET.get('page')
    try:
        notifications = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        notifications = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        notifications = paginator.page(paginator.num_pages)

    context = {'notifications': notifications}
    return render(request, 'admin_end/attendance_notif.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
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

def get_absent_users_data(request):
    # Get absent users from both tables
    timein_absent_users = TimeIn.objects.filter(is_absent=True).values('user__username').distinct()
    online_absent_users = Online.objects.filter(is_absent=True).values('user__username').distinct()
    
    # Create a set of all absent users
    absent_users = set()
    absent_users.update(user['user__username'] for user in timein_absent_users)
    absent_users.update(user['user__username'] for user in online_absent_users)

    # Prepare data for Highcharts
    absent_data = []
    for user in absent_users:
        absent_count = TimeIn.objects.filter(user__username=user, is_absent=True).count() + \
                       Online.objects.filter(user__username=user, is_absent=True).count()
        absent_data.append({'name': user, 'y': absent_count})

    return JsonResponse(absent_data, safe=False)

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# SCHEDULE API FROM SCHEDULER
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def schedule_api(request):
    api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        api_data = response.json().get('data', [])  # 'data' key holds the list of schedules
        if not api_data:
            return JsonResponse({'error_message': 'No data returned from the API'}, status=400)
        
        schedules_from_api = []
        for schedule_info in api_data:
            start_time_str = schedule_info.get('fstart_time', '')
            end_time_str = schedule_info.get('fend_time', '')
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').strftime('%I:%M %p')
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').strftime('%I:%M %p')

            schedule_data = {
                'Id': schedule_info.get('id', ''),
                'FacultyId': schedule_info.get('facultyid', ''),  
                'Day': schedule_info.get('day', ''),
                'RoomName': schedule_info.get('roomname', ''),
                'StartTime': start_time,
                'EndTime': end_time,
            }
            schedules_from_api.append(schedule_data)
        else:
            print("Failed to fetch data. Status code:", response.status_code)

        return render(request, 'admin_end/schedule_api.html', {'schedules_from_api': schedules_from_api} if schedules_from_api else {'error_message': 'Failed to fetch data from the API'})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
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
    headers = {
        'Authorization': 'API-Key',
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJrZXkiOiI1NGY0NzRmMTAxYTc0NWRhYmRiODU1M2I4YzYzMzliMSJ9.hNjCSVI3bsaivK3JlAOqGBlrMkvZxUptUxSqCCD5STs',  # Replace ' token ' with the actual token variable
    }
    response = requests.get(api_url, headers=headers)

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
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')  
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
    headers = {
        'Authorization': 'API-Key',
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJrZXkiOiI1NGY0NzRmMTAxYTc0NWRhYmRiODU1M2I4YzYzMzliMSJ9.hNjCSVI3bsaivK3JlAOqGBlrMkvZxUptUxSqCCD5STs',  # Replace ' token ' with the actual token variable
    }
    response = requests.get(api_url, headers=headers)

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
    
