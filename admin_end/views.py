from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.cache import cache_control
from django.contrib import messages
from .models import CustomUser, FacultyAccount
from faculty_end.models import Complains, TimeIn, Online, Evidence
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, date
import dateutil.parser
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
import requests

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='admin').exists()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')

def dashboard(request):
    return render(request,'admin_end/dashboard.html')

def supdashboard(request):
    return render(request,'admin_end/supdashboard.html')

def directordashboard(request):
    return render(request,'admin_end/directordashboard.html')

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

def online_approval(request):
    return render(request,'admin_end/online_approval.html')

def attendance_summary(request):
    # Retrieve TimeIn and Online data ordered by created_at descending
    time_in_data = TimeIn.objects.select_related('user').order_by('-created_at').all()
    online_data = Online.objects.select_related('user').order_by('-created_at').all()

    combined_data = []

    # Process TimeIn data
    for record in time_in_data:
        combined_data.append({
            'id': record.id,
            'user': f"{record.user.user_firstname} {record.user.user_lastname}",
            'room_name': record.room_name,
            'time_in': record.time_in,
            'time_start': record.time_start,
            'time_out': record.time_out,
            'day': record.day,
            'date': record.date,
            'month': record.month,
            'delay': record.delay,
            'status': record.status,
            'coursesection': record.coursesection,
            'remarks': record.remarks,
            'acadhead_created_at': record.acadhead_created_at,
            'created_at': record.created_at,
            'is_absent': record.is_absent,
            'is_approved': record.is_approved,
            'validation_comment': record.validation_comment,
            'source': 'Face-to-Face'
        })

    # Process Online data
    for record in online_data:
        combined_data.append({
            'id': record.id,
            'user': f"{record.user.user_firstname} {record.user.user_lastname}",
            'room_name': record.room_name,
            'time_in': record.time_in,
            'time_start': record.time_start,
            'time_out': record.time_out,
            'day': record.day,
            'date': record.date,
            'month': record.month,
            'delay': record.delay,
            'status': record.status,
            'coursesection': record.coursesection,
            'remarks': '',
            'acadhead_created_at': record.acadhead_created_at,
            'created_at': record.created_at,
            'is_absent': record.is_absent,
            'is_approved': record.is_approved,
            'validation_comment': record.validation_comment,
            'source': 'Online'
        })

    # Sort the combined data by created_at in descending order
    combined_data.sort(key=lambda x: x['created_at'], reverse=True)

    context = {'combined_data': combined_data}
    return render(request, 'admin_end/attendance_summary.html', context)

def overall(request):
    # Retrieve TimeIn and Online data ordered by created_at descending
    time_in_data = TimeIn.objects.select_related('user').order_by('-created_at').all()
    online_data = Online.objects.select_related('user').order_by('-created_at').all()

    combined_data = []

    # Process TimeIn data
    for record in time_in_data:
        combined_data.append({
            'id': record.id,
            'user': f"{record.user.user_firstname} {record.user.user_lastname}",
            'room_name': record.room_name,
            'time_in': record.time_in,
            'time_start': record.time_start,
            'time_out': record.time_out,
            'day': record.day,
            'date': record.date,
            'month': record.month,
            'delay': record.delay,
            'status': record.status,
            'coursesection': record.coursesection,
            'remarks': record.remarks,
            'validated_at': record.acadhead_created_at,
            'created_at': record.created_at,
            'is_absent': record.is_absent,
            'is_approved': record.is_approved,
            'validation_comment': record.validation_comment,
            'source': 'Face-to-Face'
        })

    # Process Online data
    for record in online_data:
        combined_data.append({
            'id': record.id,
            'user': f"{record.user.user_firstname} {record.user.user_lastname}",
            'room_name': record.room_name,
            'time_in': record.time_in,
            'time_start': record.time_start,
            'time_out': record.time_out,
            'day': record.day,
            'date': record.date,
            'month': record.month,
            'delay': record.delay,
            'status': record.status,
            'coursesection': record.coursesection,
            'remarks': '',
            'acadhead_created_at': record.acadhead_created_at,
            'created_at': record.created_at,
            'is_absent': record.is_absent,
            'is_approved': record.is_approved,
            'validation_comment': record.validation_comment,
            'source': 'Online'
        })

    # Sort the combined data by created_at in descending order
    combined_data.sort(key=lambda x: x['created_at'], reverse=True)

    context = {'combined_data': combined_data}
    return render(request, 'admin_end/overall.html', context)

def update_status(request):
    record_id = request.POST.get('record_id')
    status = request.POST.get('status')
    source = request.POST.get('source')

    if source == 'Face-to-Face':
        record = get_object_or_404(TimeIn, pk=record_id)
    else:
        record = get_object_or_404(Online, pk=record_id)
    
    record.status = status
    record.save()
    
    return redirect('overall')

def complaints_f2f(request):

    complains = Complains.objects.select_related('complainant', 'validated_by').order_by('-complained_date')
    evidences = Evidence.objects.select_related('uploaded_by').all()

    context = {
        'complains': complains,
        'evidences': evidences
    }

    return render(request, 'admin_end/complaints_f2f.html', context)

def onlineqrcode(request):
    return render(request,'admin_end/onlineqrcode.html')

def get_users_data(request, status):
    # Calculate the date range for the past 7 days
    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    if status == "present":
        # Query present users for the past 7 days
        present_users = TimeIn.objects.filter(
            status="Present",
            created_at__date__range=[seven_days_ago, today]
        ).values(
            'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
        ).annotate(count=Count('user'))

    elif status == "absent":
        # Query absent users for the past 7 days
        absent_users = TimeIn.objects.filter(
            status="Absent",
            created_at__date__range=[seven_days_ago, today]
        ).values(
            'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
        ).annotate(count=Count('user'))

    # Format the data as required
    data = [
        {
            'name': f"{user['user__user_firstname']} {' ' + user['user__user_middlename'] if user['user__user_middlename'] else ''} {user['user__user_lastname']} {' ' + user['user__extension_name'] if user['user__extension_name'] else ''}",
            'y': user['count']
        }
        for user in (present_users if status == "present" else absent_users)
    ]

    return JsonResponse(data, safe=False)

def absent_users_chart(request):
    today = date.today()

    absent_users_timein = TimeIn.objects.filter(
        status="Absent",
        user__user_role="faculty",
        created_at__date=today
    ).values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    absent_users_online = Online.objects.filter(
        status="Absent",
        user__user_role="faculty",
        created_at__date=today
    ).values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    # Merge the results from both queries
    absent_users = list(absent_users_timein) + list(absent_users_online)

    data = [
        {
            'name': f"{user['user__user_firstname']} {' ' + user['user__user_middlename'] if user['user__user_middlename'] else ''} {user['user__user_lastname']} {' ' + user['user__extension_name'] if user['user__extension_name'] else ''}",
            'y': user['count']
        }
        for user in absent_users
    ]

    return JsonResponse(data, safe=False)

def present_users_chart(request):
    today = date.today()

    present_users_timein = TimeIn.objects.filter(
        status="Present",
        user__user_role="faculty",
        created_at__date=today
    ).values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    present_users_online = Online.objects.filter(
        status="Present",
        user__user_role="faculty",
        created_at__date=today
    ).values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    # Merge the results from both queries
    present_users = list(present_users_timein) + list(present_users_online)

    data = [
        {
            'name': f"{user['user__user_firstname']} {' ' + user['user__user_middlename'] if user['user__user_middlename'] else ''} {user['user__user_lastname']} {' ' + user['user__extension_name'] if user['user__extension_name'] else ''}",
            'y': user['count']
        }
        for user in present_users
    ]

    return JsonResponse(data, safe=False)

def supabsent_users_chart(request):
    absent_users_timein = TimeIn.objects.filter(status="Absent", user__user_role="faculty").values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    absent_users_online = Online.objects.filter(status="Absent", user__user_role="faculty").values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    # Merge the results from both queries
    absent_users = list(absent_users_timein) + list(absent_users_online)

    data = [
        {
            'name': f"{user['user__user_firstname']} {' ' + user['user__user_middlename'] if user['user__user_middlename'] else ''} {user['user__user_lastname']} {' ' + user['user__extension_name'] if user['user__extension_name'] else ''}",
            'y': user['count']
        }
        for user in absent_users
    ]

    return JsonResponse(data, safe=False)

def suppresent_users_chart(request):
    present_users_timein = TimeIn.objects.filter(status="Present", user__user_role="faculty").values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    present_users_online = Online.objects.filter(status="Present", user__user_role="faculty").values(
        'user__user_firstname', 'user__user_middlename', 'user__user_lastname', 'user__extension_name'
    ).annotate(count=Count('user'))

    # Merge the results from both queries
    present_users = list(present_users_timein) + list(present_users_online)

    data = [
        {
            'name': f"{user['user__user_firstname']} {' ' + user['user__user_middlename'] if user['user__user_middlename'] else ''} {user['user__user_lastname']} {' ' + user['user__extension_name'] if user['user__extension_name'] else ''}",
            'y': user['count']
        }
        for user in present_users
    ]

    return JsonResponse(data, safe=False)

@user_passes_test(is_superadmin, login_url='error_400')
@login_required(login_url='login_as')
def admin_settings(request):
    return render(request,'admin_end/admin_settings.html')

def directorsettings(request):
    return render(request,'admin_end/directorsettings.html')

def headsettings(request):
    return render(request,'admin_end/headsettings.html')
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

def merged_table(request):
    # Fetch data from both tables
    time_in_data = TimeIn.objects.all()
    online_data = Online.objects.all()

    complains = Complains.objects.all()

    # Merge data from both tables
    merged_data = list(time_in_data) + list(online_data)

    # Sort merged data by date
    merged_data.sort(key=lambda x: x.created_at)

    # Pass the merged data to the template for rendering
    return render(request, 'admin_end/merged_table.html', {'merged_data': merged_data, 'complains': complains})

def supmerged_table(request):
    # Fetch data from both tables
    time_in_data = TimeIn.objects.all()
    online_data = Online.objects.all()

    # Merge data from both tables
    merged_data = list(time_in_data) + list(online_data)

    # Sort merged data by date
    merged_data.sort(key=lambda x: x.created_at)

    # Pass the merged data to the template for rendering
    return render(request, 'admin_end/supmerged_table.html', {'merged_data': merged_data})
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
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
def log_time_in(request):
    room_name = request.GET.get('room')
    return render(request, 'log_time_in.html', {'room_name': room_name})
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
            if user.user_role == 'admin':
                login(request, user)
                messages.success(request, 'Admin logged in successful.')
                return redirect('dashboard')  # Redirect to admin dashboard
            
            elif user.user_role == 'superadmin':
                login(request, user)
                messages.success(request, 'Faculty logged in successful.')
                return redirect('supdashboard')  # Redirect to dashboard page
            
            elif user.user_role == 'faculty':
                login(request, user)
                messages.success(request, 'Faculty logged in successful.')
                return redirect('log_time_in')  # Redirect to face to face time in page
            
            elif user.user_role == 'Academic Head':
                login(request, user)
                messages.success(request, 'Academic Head logged in successful.')
                return redirect('complaints_f2f')  # Redirect to face to face complaints page
            
            elif user.user_role == 'Director':
                login(request, user)
                messages.success(request, 'Director logged in successful.')
                return redirect('directordashboard')  # Redirect to dashboard
            
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
def merged_table(request):
    # Fetch data from both tables
    time_in_data = TimeIn.objects.all()
    online_data = Online.objects.all()

    # Add source attribute to each record
    for record in time_in_data:
        record.source = 'Face-to-Face'
    for record in online_data:
        record.source = 'Online'

    # Merge data from both tables
    merged_data = list(time_in_data) + list(online_data)

    # Sort merged data by date (newest to oldest)
    merged_data.sort(key=lambda x: x.created_at, reverse=True)

    # Pass the merged data to the template for rendering
    return render(request, 'admin_end/merged_table.html', {'merged_data': merged_data})



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
    
@login_required
def user_attendance_view(request):
    # Order attendance records by 'created_at' in descending order
    attendance_records = Online.objects.select_related('user').order_by('-created_at')

    data = []
    for record in attendance_records:
        evidences = record.online_evidence.all()
        data.append({
            'id': record.pk,
            'user_firstname': record.user.user_firstname,
            'user_lastname': record.user.user_lastname,
            'is_absent': record.is_absent,
            'status': record.status,
            'evidences': [evidence.evidence.url for evidence in evidences],
            'date': record.date,
            'validation_comment': record.validation_comment,
            'acadhead_created_at': record.acadhead_created_at,
            'created_at': record.created_at
        })

    return render(request, 'admin_end/online_approval.html', {'data': data})

@login_required
def disapprove_attendance(request, online_id):
    if request.method == 'POST':
        online_record = get_object_or_404(Online, pk=online_id)
        remarks = request.POST.get('remarks', '') 

        online_record.status = 'Absent'
        online_record.validation_comment = f"Disapproved by {request.user.get_full_name()}: {remarks}"
        online_record.acadhead_created_at = timezone.now()  # Set the current timestamp
        online_record.save()
        return redirect('user_attendance')
    else:
        return redirect('user_attendance')

@login_required
def approve_attendance(request, online_id):
    online_record = get_object_or_404(Online, pk=online_id)
    online_record.status = 'Present'
    online_record.validation_comment = f"Approved by {request.user.get_full_name()}"
    online_record.acadhead_created_at = timezone.now()
    online_record.save()
    return redirect('user_attendance')
