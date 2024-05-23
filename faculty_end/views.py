# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LeaveApplication, TimeIn, TimeOut, Online
from django.contrib.auth import authenticate, login, logout
from admin_end.models import FacultyShift, CustomUser, LeaveApplicationAction
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
import requests
from django.utils import timezone
from django.http import HttpResponse

def is_faculty(user):
    return user.is_authenticated and not user.is_superuser

def log_time_in(request):
    return render(request,'faculty_end/log_time_in.html')

@login_required
def faculty_attendance(request):
    user = request.user
    if user.user_role != 'faculty':
        return render(request, 'not_authorized.html')

    time_in_records = TimeIn.objects.filter(user=user)
    online_records = Online.objects.filter(user=user)

    # Combine records with an identifier for their source
    attendance_records = [
        {'type': 'TimeIn', 'record': record} for record in time_in_records
    ] + [
        {'type': 'Online', 'record': record} for record in online_records
    ]

    context = {
        'attendance_records': attendance_records,
    }

    return render(request, 'faculty_end/faculty_attendance.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def leaveapp_create(request):
    if request.method == 'POST':
        # Retrieve form data from the request
        user = request.user
        department = request.POST.get('department')
        full_name = request.POST.get('full_name')
        filing_date = datetime.strptime(request.POST.get('filing_date'), '%Y-%m-%d').date()
        position = request.POST.get('position')
        salary = request.POST.get('salary')
        leave_type = request.POST.get('leave_type')
        specify_leavetype = request.POST.get('specify_leavetype', '')
        leave_details = request.POST.get('leave_details')
        specify_leavedetails = request.POST.get('specify_leavedetails', '')
        days_number = request.POST.get('days_number')
        commutation = request.POST.get('commutation')
        inclusive_dates = request.POST.get('inclusive_dates')
        signature = request.POST.get('signature')

        # Create the LeaveApplication object
        leave_application = LeaveApplication.objects.create(
            user=user,
            department=department,
            full_name=full_name,
            filing_date=filing_date,
            position=position,
            salary=salary,
            leave_type=leave_type,
            specify_leavetype=specify_leavetype,
            leave_details=leave_details,
            specify_leavedetails=specify_leavedetails,
            days_number=days_number,
            commutation=commutation,
            inclusive_dates=inclusive_dates,
            signature=signature,
            created=timezone.now()  # Set the created field to current time
        )

        # Optionally, you can perform some additional actions here
        # For example, you can render a success page or redirect the user
        messages.success(request, 'Leave application submitted successfully!')
        return redirect('leaveapp_list')
    else:
        # Handle GET request (render the form)
        return render(request, 'faculty_end/leaveapp_create.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def leaveapp_list(request):
    # Assuming you have a way to identify the current user (faculty member)
    current_user = request.user

    # Fetch leave applications for the current user
    all_leave_applications = LeaveApplication.objects.filter(user=current_user)

    # Fetch leave application actions for the current user
    all_leave_actions = LeaveApplicationAction.objects.filter(leave_application__user=current_user)

    # Include Date Submitted from LeaveApplication model for all actions
    actions_with_date = []
    for action in all_leave_actions:
        status = action.status if action.status else 'No Status'  # Handle cases where status is empty or None
        actions_with_date.append({
            'action': action,
            'date_submitted': action.leave_application.created,  # Accessing the Date Submitted from LeaveApplication
            'status': status,  # Include status in the context
        })

    return render(request, 'faculty_end/leaveapp_list.html', {'leave_apps': all_leave_applications, 'actions_with_date': actions_with_date})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def leaveapp_view(request, leave_app_id):
    # Fetch the leave application object using the leave_app_id
    leave_application = get_object_or_404(LeaveApplication, pk=leave_app_id)
    
    # Fetch the related LeaveApplicationAction (assuming there's only one related action per application)
    leave_action = LeaveApplicationAction.objects.filter(leave_application=leave_application).first()

    return render(request, 'faculty_end/leaveapp_view.html', {'leave_application': leave_application, 'leave_action': leave_action})

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
            return redirect('faculty_attendance')
        else:
            messages.error(request, 'Incorrect credentials or user is not a faculty member.')
            return render(request, 'faculty_end/faculty_login.html')

    return render(request, 'faculty_end/faculty_login.html')

@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def faculty_logout(request):
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def qrcode_generator(request):
    return render(request,'faculty_end/qrcode_generator.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def account_settings(request):
    return render(request,'faculty_end/account_settings.html')

def error_400(request):
    return render(request,'faculty_end/error_400.html')

# def log_time_in(request):
#     # Get the faculty ID from your model based on the logged-in user or any other relevant context
#     # For example:
#     faculty_id = request.user.facultyaccount.faculty_id  # Assuming the faculty ID is stored in the FacultyAccount model related to the user

#     # Fetch data from the API
#     api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
#     access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

#     headers = {
#         'Authorization': f'Bearer {access_token}',
#     }

#     response = requests.get(api_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the API response
#         api_data = response.json()
#         room_name = api_data.get('roomname', None)

#         if room_name:
#             # Get other required data
#             time_in = datetime.now().strftime('%H:%M:%S')  # Current time
#             date = datetime.now().strftime('%Y-%m-%d')     # Current date
#             month = datetime.now().strftime('%B')          # Current month

#             # Render the template with the fetched data
#             return render(request, 'faculty_end/log_time_in.html', {
#                 'time_in': time_in,
#                 'date': date,
#                 'month': month,
#                 'room_name': room_name,
#                 'faculty_id': faculty_id  # Pass the faculty ID to the template
#             })
#         else:
#             # Handle case where room name is not available from API
#             return render(request, 'faculty_end/log_time_in.html', {
#                 'error_message': 'Room name not found in API response.'
#             })
#     else:
#         # Handle API request failure
#         return render(request, 'faculty_end/log_time_in.html', {
#             'error_message': 'Failed to fetch room name from API.'
#         })
def attendance_record(request):
    try:
        # Fetch all time data
        faculty_data = TimeIn.objects.all().values(
            'room_name', 'time_in', 'time_out', 'day', 'date', 'month', 'delay', 'status', 'is_absent'
        ).union(
            Online.objects.all().values(
                'room_name', 'time_in', 'time_out', 'day', 'date', 'month', 'delay', 'status', 'is_absent'
            )
        )

        print("Faculty Data:", faculty_data)  # Print fetched data for debugging
        
        return render(request, 'attendance_record.html', {'faculty_data': faculty_data})
    except Exception as e:
        print("Error fetching data:", e)  # Print any errors for debugging
        return render(request, 'empty.html')  # Render an empty page for simplicity

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_as')
@user_passes_test(is_faculty, login_url='error_400')
def log_time_in(request):
    if request.method == 'POST':
        # Handle form submission
        day = request.POST.get('day')
        time_in_str = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        room_name = request.POST.get('room_name')
        date = request.POST.get('date')
        month = request.POST.get('month')

        # Convert time_in to datetime object
        time_in = datetime.strptime(time_in_str, '%H:%M')

        # Get faculty's fstart_time from the API
        faculty_id = request.user.facultyaccount.faculty_id
        current_day = datetime.now().strftime('%A')

        api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            api_data = response.json().get('data', [])
            if not api_data:
                return render(request, 'faculty_end/log_time_in.html', {'error_message': 'No data returned from the API'})

            # Find the matching schedule
            matching_schedule = None
            for schedule in api_data:
                if schedule.get('facultyid') == faculty_id and schedule.get('day') == current_day:
                    matching_schedule = schedule
                    break
            
            if matching_schedule:
                fstart_time_str = matching_schedule.get('fstart_time')
                fstart_time = datetime.strptime(fstart_time_str, '%H:%M:%S')

                # Compute the difference between time_in and fstart_time
                time_difference = time_in - fstart_time
                delay_minutes = max(time_difference.total_seconds() / 60, 0)

                # Determine if the user is late
                if delay_minutes > 0:
                    delay = f"{int(delay_minutes)} minute{'s' if delay_minutes > 1 else ''} Late"
                else:
                    delay = None
            else:
                # If there's no matching schedule, consider the user as on time
                delay = None

            # Save the data to the database with status "Present"
            TimeIn.objects.create(
                user=request.user,
                day=day,
                time_in=time_in_str,
                time_out=time_out,
                room_name=room_name,
                date=date,
                month=month,
                delay=delay,
                status="Present"
            )

            messages.success(request, 'Logged in successfully')
            return redirect('faculty_attendance')
        else:
            return render(request, 'faculty_end/log_time_in.html', {'error_message': 'Failed to fetch data from the API'})

    else:
        # Get faculty ID and current day
        faculty_id = request.user.facultyaccount.faculty_id
        current_day = datetime.now().strftime('%A')

        # Fetch data from the API
        api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            api_data = response.json().get('data', [])
            if not api_data:
                return render(request, 'faculty_end/log_time_in.html', {'error_message': 'No data returned from the API'})

            # Filter schedules based on the matching faculty ID and current day
            schedules_from_api = [schedule for schedule in api_data if schedule.get('facultyid') == faculty_id and schedule.get('day') == current_day]

            # Process the schedules to display StartTime and EndTime
            processed_schedules = []
            for schedule_info in schedules_from_api:
                start_time_str = schedule_info.get('fstart_time', '')
                end_time_str = schedule_info.get('fend_time', '')
                start_time = datetime.strptime(start_time_str, '%H:%M:%S').strftime('%I:%M %p')
                end_time = datetime.strptime(end_time_str, '%H:%M:%S').strftime('%I:%M %p')

                schedule_data = {
                    'Id': schedule_info.get('id', ''),
                    'FacultyId': schedule_info.get('facultyid', ''),
                    'Day': schedule_info.get('day', ''),
                    'StartTime': start_time,
                    'EndTime': end_time,
                    'RoomName': schedule_info.get('roomname', '')
                }
                processed_schedules.append(schedule_data)

            # Pass the schedules and the current date info to the template
            current_time = datetime.now().strftime('%H:%M')
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_month = datetime.now().strftime('%B')

            # Extract the end_time from the first schedule (if any) for the initial time_out value
            initial_end_time_str = schedules_from_api[0].get('fend_time', '') if schedules_from_api else ''
            if initial_end_time_str:
                initial_time_out = datetime.strptime(initial_end_time_str, '%H:%M:%S').strftime('%H:%M')
            else:
                initial_time_out = ''

            return render(request, 'faculty_end/log_time_in.html', {
                'schedules': processed_schedules,
                'current_day': current_day,
                'current_time': current_time,
                'current_date': current_date,
                'current_month': current_month,
                'initial_time_out': initial_time_out,  # Pass the initial time_out value to the template
            })
        else:
            return render(request, 'faculty_end/log_time_in.html', {'error_message': 'Failed to fetch data from the API'})
        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_as')
@user_passes_test(is_faculty, login_url='error_400')  
def online_time_in(request):
    if request.method == 'POST':
        # Handle form submission
        day = request.POST.get('day')
        time_in_str = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        room_name = request.POST.get('room_name')
        date = request.POST.get('date')
        month = request.POST.get('month')
        
        # Parse time_in to datetime object
        time_in = datetime.strptime(time_in_str, '%H:%M').time()

        # Fetch faculty's fstart_time from the API
        faculty_id = request.user.facultyaccount.faculty_id
        current_day = datetime.now().strftime('%A')
        api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            api_data = response.json().get('data', [])
            if not api_data:
                return render(request, 'faculty_end/online_time_in.html', {'error_message': 'No data returned from the API'})

            # Find the faculty's schedule for the current day
            faculty_schedule = next((schedule for schedule in api_data if schedule.get('facultyid') == faculty_id and schedule.get('day') == current_day), None)
            if faculty_schedule:
                fstart_time_str = faculty_schedule.get('fstart_time', '')
                fstart_time = datetime.strptime(fstart_time_str, '%H:%M:%S').time()

                # Compute the delay
                delay_minutes = (datetime.combine(datetime.min, time_in) - datetime.combine(datetime.min, fstart_time)).seconds // 60
                if delay_minutes > 0:
                    delay = f"{delay_minutes} minute{'s' if delay_minutes > 1 else ''} Late"
                else:
                    delay = None
            else:
                delay = None
        else:
            return render(request, 'faculty_end/online_time_in.html', {'error_message': 'Failed to fetch data from the API'})

        # Status should be "Present" when time_in is logged
        status = 'Present'

        # Set is_absent to False when status is Present
        is_absent = False

        # Save the data to the database
        Online.objects.create(
            user=request.user,
            day=day,
            time_in=time_in_str,
            time_out=time_out,
            room_name=room_name,
            date=date,
            month=month,
            delay=delay,
            status=status, 
            is_absent=is_absent, 
            evidence=request.FILES.get('evidence'),  # Handle file upload
        )

        # Redirect to the online_time_in view
        messages.success(request, 'Logged in successfully')
        return redirect('faculty_attendance')  # Replace 'online_time_in' with the actual URL name of your view
    else:
        # Retrieve the faculty ID and current day
        faculty_id = request.user.facultyaccount.faculty_id
        current_day = datetime.now().strftime('%A')

        # Fetch data from the API
        api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            api_data = response.json().get('data', [])
            if not api_data:
                return render(request, 'faculty_end/online_time_in.html', {'error_message': 'No data returned from the API'})

            # Filter schedules based on the matching faculty ID and current day
            schedules_from_api = [schedule for schedule in api_data if schedule.get('facultyid') == faculty_id and schedule.get('day') == current_day]

            # Process the schedules to display StartTime and EndTime
            processed_schedules = []
            for schedule_info in schedules_from_api:
                start_time_str = schedule_info.get('fstart_time', '')
                end_time_str = schedule_info.get('fend_time', '')
                start_time = datetime.strptime(start_time_str, '%H:%M:%S').strftime('%I:%M %p')
                end_time = datetime.strptime(end_time_str, '%H:%M:%S').strftime('%I:%M %p')

                schedule_data = {
                    'Id': schedule_info.get('id', ''),
                    'FacultyId': schedule_info.get('facultyid', ''),
                    'Day': schedule_info.get('day', ''),
                    'StartTime': start_time,
                    'EndTime': end_time,
                    'RoomName': schedule_info.get('roomname', '')
                }
                processed_schedules.append(schedule_data)

            # Pass the schedules and the current date info to the template
            current_time = datetime.now().strftime('%H:%M')
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_month = datetime.now().strftime('%B')

            # Extract the end_time from the first schedule (if any) for the initial time_out value
            initial_end_time_str = schedules_from_api[0].get('fend_time', '') if schedules_from_api else ''
            if initial_end_time_str:
                initial_time_out = datetime.strptime(initial_end_time_str, '%H:%M:%S').strftime('%H:%M')
            else:
                initial_time_out = ''

            return render(request, 'faculty_end/online_time_in.html', {
                'schedules': processed_schedules,
                'current_day': current_day,
                'current_time': current_time,
                'current_date': current_date,
                'current_month': current_month,
                'initial_time_out': initial_time_out,  # Pass the initial time_out value to the template
            })
        else:
            return render(request, 'faculty_end/online_time_in.html', {'error_message': 'Failed to fetch data from the API'})
        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def log_attendance(request):
    # Get the faculty ID from your model based on the logged-in user or any other relevant context
    # For example:
    faculty_id = request.user.facultyaccount.faculty_id  # Assuming the faculty ID is stored in the FacultyAccount model related to the user

    # Get the current day in the format 'Monday', 'Tuesday', etc.
    current_day = datetime.now().strftime('%A')

    # Fetch data from the API
    api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        api_data = response.json().get('data', [])  # 'data' key holds the list of schedules
        if not api_data:
            return render(request, 'faculty_end/attendance_record.html', {'error_message': 'No data returned from the API'})

        # Filter schedules based on the matching faculty ID and current day
        schedules_from_api = [schedule for schedule in api_data if schedule.get('facultyid') == faculty_id and schedule.get('day') == current_day]

        # Process the schedules to display StartTime and EndTime
        processed_schedules = []
        for schedule_info in schedules_from_api:
            start_time_str = schedule_info.get('fstart_time', '')
            end_time_str = schedule_info.get('fend_time', '')
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').strftime('%I:%M %p')
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').strftime('%I:%M %p')

            schedule_data = {
                'Id': schedule_info.get('id', ''),
                'FacultyId': schedule_info.get('facultyid', ''),
                'Day': schedule_info.get('day', ''),
                'StartTime': start_time,
                'EndTime': end_time,
            }
            processed_schedules.append(schedule_data)

        return render(request, 'faculty_end/log_attendance.html', {'schedules': processed_schedules, 'current_day': current_day})
    else:
        return render(request, 'faculty_end/log_attendance.html', {'error_message': 'Failed to fetch data from the API'})
    
def attendance_record1(request):
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
    return render(request, 'faculty_end/attendance_record1.html', {'faculty_shifts': faculty_shifts, 'current_date': current_date})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='faculty_login')
@user_passes_test(is_faculty, login_url='error_400')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        # Check if the old password is correct
        if not request.user.check_password(old_password):
            messages.error(request, 'Incorrect old password.')
            return redirect('account_settings')

        # Check if the new passwords match
        if password != repassword:
            messages.error(request, 'New passwords do not match.')
            return redirect('account_settings')

        # Update the user's password
        request.user.set_password(password)
        request.user.save()

        # Update the session to avoid logout
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        return redirect('account_settings')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('faculty_end/account_settings')
    
def time_in_out_records(request, faculty_shift_id):
    faculty_shift = get_object_or_404(FacultyShift, pk=faculty_shift_id)
    user = request.user
    
    # Fetch time in and time out records for the faculty shift
    time_in_records = TimeIn.objects.filter(user=user, faculty_shift=faculty_shift).order_by('date', 'time_in')
    time_out_records = TimeOut.objects.filter(user=user, faculty_shift=faculty_shift).order_by('date', 'time_out')

    # Merge time in and time out records into a single list and sort them by date and time
    all_records = []
    in_index = out_index = 0

    # Merge time in and time out records alternatively
    while in_index < len(time_in_records) and out_index < len(time_out_records):
        if time_in_records[in_index].date <= time_out_records[out_index].date:
            all_records.append(time_in_records[in_index])
            in_index += 1
        else:
            all_records.append(time_out_records[out_index])
            out_index += 1

    all_records.extend(time_in_records[in_index:])
    all_records.extend(time_out_records[out_index:])

    return render(request, 'faculty_end/attendance_record.html', {'faculty_shift': faculty_shift, 'records': all_records})

# def log_time_in(request):
#     if request.method == 'POST':
#         location = request.POST.get('location')
#         date = datetime.now().date()
#         time_in = datetime.now().time()

#         # Fetch the start time for the faculty's schedule from the API
#         api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
#         access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

#         headers = {
#             'Authorization': f'Bearer {access_token}',
#         }

#         response = requests.get(api_url, headers=headers)

#         if response.status_code == 200:
#             api_data = response.json().get('data', [])  # 'data' key holds the schedule start time
#             if not api_data:
#                 start_time = None  # No data returned from API
#             else:
#                 # Assuming 'fstart_time' is the key for start time in API response
#                 start_time_str = api_data[0].get('fstart_time', '')
#                 start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None

#             # Compute the status based on the start time and current time
#             if start_time is None:
#                 status = 'No Schedule'  # If no start time found
#             else:
#                 # Convert time_in and start_time to datetime objects
#                 time_in_datetime = datetime.combine(date, time_in)
#                 start_time_datetime = datetime.combine(date, start_time)

#                 # Compute the difference in minutes
#                 time_difference_seconds = (time_in_datetime - start_time_datetime).total_seconds()

#                 # Set the status based on the time difference
#                 if time_difference_seconds < 0:
#                     status = 'Early'
#                 elif time_difference_seconds > 0:
#                     status = 'Late'
#                 else:
#                     status = 'On time'

#             # Save the TimeIn record
#             TimeIn.objects.create(user=request.user, location=location, date=date, time_in=time_in, status=status)

#             messages.success(request, 'Time in logged successfully')
#             return redirect('attendance_record')  # Redirect to the attendance record page after logging time in
#         else:
#             return render(request, 'faculty_end/log_time_in.html', {'error_message': 'Failed to fetch start time from API'})

#     return render(request, 'faculty_end/log_time_in.html')

def log_time_out(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        date = datetime.now().date()
        time_out = datetime.now().time()

        # Fetch the end time for the faculty's schedule from the API
        api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            api_data = response.json().get('data', [])  # 'data' key holds the schedule end time
            if not api_data:
                end_time = None  # No data returned from API
            else:
                # Assuming 'fend_time' is the key for end time in API response
                end_time_str = api_data[0].get('fend_time', '')
                end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None

            # Compute the status based on the end time and current time
            if end_time is None:
                status = 'No Schedule'  # If no end time found
            else:
                # Convert time_out and end_time to datetime objects
                time_out_datetime = datetime.combine(date, time_out)
                end_time_datetime = datetime.combine(date, end_time)

                # Compute the difference in minutes
                time_difference_minutes = int((time_out_datetime - end_time_datetime).total_seconds() / 60)

                # Set the status based on the time difference
                if time_difference_minutes < 0:
                    status = 'Early'
                elif time_difference_minutes > 0:
                    status = 'Late'
                else:
                    status = 'On time'

            # Save the TimeOut record
            TimeOut.objects.create(user=request.user, location=location, date=date, time_out=time_out, status=status)

            messages.success(request, 'Time out logged successfully')
            return redirect('attendance_record')  # Redirect to the attendance record page after logging time out
        else:
            return render(request, 'faculty_end/log_time_out.html', {'error_message': 'Failed to fetch end time from API'})

    return render(request, 'faculty_end/log_time_out.html')

def log_time_out(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        date = datetime.now().date()
        time_out = datetime.now().time()

        # Fetch the end time for the faculty's schedule from the API
        api_url = 'https://schedulerserver-6e565d991c10.herokuapp.com/facultyloadings/getfacultyloading'
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYW1lc0BzYW5kbG90LnBoIiwidXNlcnR5cGUiOiJzdGFmZiIsImV4cCI6MTcxNzYxMjgzNH0.0NDFuxsVNh40fsIVf8b2H_4OBSdm0LPRPdUDpkf8NxE'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            api_data = response.json().get('data', [])  # 'data' key holds the schedule end time
            if not api_data:
                end_time = None  # No data returned from API
            else:
                # Assuming 'fend_time' is the key for end time in API response
                end_time_str = api_data[0].get('fend_time', '')
                end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None

            # Compute the status based on the end time and current time
            if end_time is None:
                status = 'No Schedule'  # If no end time found
            else:
                # Convert time_out and end_time to datetime objects
                time_out_datetime = datetime.combine(date, time_out)
                end_time_datetime = datetime.combine(date, end_time)

                # Compute the difference in minutes
                time_difference_minutes = int((time_out_datetime - end_time_datetime).total_seconds() / 60)

                # Set the status based on the time difference
                if time_difference_minutes < 0:
                    status = f'{abs(time_difference_minutes)} minute/s early'
                elif time_difference_minutes > 0:
                    status = f'{time_difference_minutes} minute/s overtime'
                else:
                    status = 'On time'

            # Save the TimeOut record
            TimeOut.objects.create(user=request.user, location=location, date=date, time_out=time_out, status=status)

            messages.success(request, 'Time out logged successfully')
            return redirect('attendance_record')  # Redirect to the attendance record page after logging time out
        else:
            return render(request, 'faculty_end/log_time_out.html', {'error_message': 'Failed to fetch end time from API'})

    return render(request, 'faculty_end/log_time_out.html')

def attendance_record(request):
    # Default filter by last 7 days
    filter_option = request.GET.get('filter', 'last_7_days')
    
    # Get the start date based on filter option
    if filter_option == 'last_7_days':
        start_date = datetime.now() - timedelta(days=7)
    elif filter_option == 'last_month':
        start_date = datetime.now() - timedelta(days=30)
    else:
        start_date = None
    
    # Query TimeIn and TimeOut based on start date and merge them
    if start_date:
        time_in_data = TimeIn.objects.filter(date__gte=start_date)
        time_out_data = TimeOut.objects.filter(date__gte=start_date)
    else:
        time_in_data = TimeIn.objects.all()
        time_out_data = TimeOut.objects.all()
    
    # Merge TimeIn and TimeOut data
    merged_data = sorted(list(time_in_data) + list(time_out_data), key=lambda x: x.date)
    
    context = {
        'merged_data': merged_data,
        'filter_option': filter_option,
    }
    return render(request, 'faculty_end/attendance_record.html', context)