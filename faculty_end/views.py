# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Complains, Evidence, TimeIn, TimeOut, Online
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
import requests
from django.utils import timezone
from datetime import date
from django.http import JsonResponse

def is_faculty(user):
    return user.is_authenticated and not user.is_superuser

def log_time_in(request):
    return render(request,'faculty_end/log_time_in.html')

def error_message(request):
    return render(request,'faculty_end/error_message.html')

@login_required
def faculty_attendance(request):
    user = request.user
    if user.user_role != 'faculty':
        return render(request, 'not_authorized.html')

    time_in_records = TimeIn.objects.filter(user=user)
    online_records = Online.objects.filter(user=user)
    online_evidences = Evidence.objects.filter(uploaded_by=user)

    attendance_records = [
        {'type': 'TimeIn', 'record': record} for record in time_in_records
    ]

    for online_record in online_records:
        evidences = Evidence.objects.filter(online=online_record)  # Get evidences related to this online_record
        attendance_records.append({'type': 'Online', 'record': online_record, 'evidences': evidences})


    context = {
        'attendance_records': attendance_records,
        'online_evidences': online_evidences,
    }

    return render(request, 'faculty_end/faculty_attendance.html', context)

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
        day = request.POST.get('day')
        time_in_str = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        room_name = request.POST.get('room_name')
        date = request.POST.get('date')
        month = request.POST.get('month')
        coursesection = request.POST.get('coursesection')
        remarks = request.POST.get('remarks')
        # Check if there is an existing record in the timein model  
        is_TimedIn = TimeIn.objects.filter(user=request.user, date=date, room_name = room_name).exists()

        if is_TimedIn:
            return redirect('log_time_in')
        
        else:
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
                api_roomname = None
                if matching_schedule:
                    fstart_time_str = matching_schedule.get('fstart_time')
                    api_roomname = matching_schedule.get('roomname')
                    fstart_time = datetime.strptime(fstart_time_str, '%H:%M:%S')

                    # Compute the difference between time_in and fstart_time
                    time_difference = time_in - fstart_time
                    delay_minutes = max(time_difference.total_seconds() / 60, 0)

                    # Determine if the user is late
                    if delay_minutes > 0:
                        delay = f"{int(delay_minutes)} minute{'s' if delay_minutes > 1 else ''} Late"
                    else:
                        delay = 'N/A'
                else:
                    delay = 'N/A'


                if api_roomname == None:
                          # Produce an error message
                    print('may error nanaman pare')
                    messages.error(request, 'There is no schedule today.')
                    return redirect('log_time_in')
                    # JsonResponse({'error': 'There is no schedule today.'}, status=400)
                    # pass

                elif api_roomname == room_name:

                    TimeIn.objects.create(
                        user=request.user,
                        day=day,
                        time_in=time_in_str,
                        time_start = fstart_time_str,
                        time_out=time_out,
                        room_name=room_name,
                        date=date,
                        month=month,
                        delay=delay,
                        coursesection=coursesection,
                        remarks=remarks,
                        status="Present",
                        is_absent = False,
                    )

                    messages.success(request, 'Logged in successfully')
                    return redirect('faculty_attendance')
                

                elif api_roomname != room_name or room_name is None:
                    # Produce an error message with api_roomname
                    error_message = f'The schedule ({api_roomname}) is not yours.'
                    messages.error(request, error_message)
                    # Redirect to error_message.html with the error message
                    return render(request, 'faculty_end/error_message.html', {'error_message': error_message, 'api_roomname': api_roomname})
                
            else:
                print("May error sa API PARE")
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

                # Get RoomName (this line is already correct)
                room_name = schedule_info.get('roomname', '')


                schedule_data = {
                    'Id': schedule_info.get('id', ''),
                    'FacultyId': schedule_info.get('facultyid', ''),
                    'Day': schedule_info.get('day', ''),
                    'StartTime': start_time,
                    'EndTime': end_time,
                    # 'RoomName': schedule_info.get('roomname', ''),
                    'ClassName': schedule_info.get('classname', ''),
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

            initial_start_time_str = schedules_from_api[0].get('fstart_time', '') if schedules_from_api else ''
            if initial_start_time_str:
                initial_time_in = datetime.strptime(initial_start_time_str, '%H:%M:%S').strftime('%H:%M')
            else:
                initial_time_in = ''

            # If the api has contents, then it will run the below code.
            rejected_complaint = False
            logged_but_absent = False
            TimeIn_record_id = 0
            complain_record = None

            if schedules_from_api:
                philippine_timezone = timezone.get_current_timezone()  # Get the current time zone setting (from settings.py)
                now = timezone.now()  # Get current time in UTC
                local_time = now.astimezone(philippine_timezone) # Convert to Philippine time
                date = local_time.date()  # Extract the date
                # Check if the user already timed in

                print('HAHHAHHAHAHA :', date, room_name)    
                is_TimeLogged = TimeIn.objects.filter(user=request.user, date=date, room_name = room_name).exists()

                if is_TimeLogged:
                    record = TimeIn.objects.get(user=request.user, date=date, room_name = room_name)
                    complain = Complains.objects.filter(onsite_id=record.id).exists()

                    time_logged = True

                    # Check if the time in record is considered as absent or have an absent status
                    if record.is_absent:
                        logged_but_absent = True
                        TimeIn_record_id = record.id
                        complain = Complains.objects.filter(onsite_id=record.id).exists()

                        if complain:
                            complain_record = Complains.objects.get(onsite_id=record.id)

                            if complain_record.is_resolved == False:
                                rejected_complaint = True


                else:
                    time_logged = False

            else:
                time_logged = None
                # If the user already timed in, just make the time_logged true for front end purposes

            return render(request, 'faculty_end/log_time_in.html', {
                'schedules': processed_schedules,
                'current_day': current_day,
                'current_time': current_time,
                'current_date': current_date,
                'current_month': current_month,
                'initial_time_out': initial_time_out,
                'initial_time_in': initial_time_in,
                'time_logged': time_logged, 
                'logged_but_absent': logged_but_absent,
                'TimeIn_record_id': TimeIn_record_id,
                'rejected_complaint': rejected_complaint,
                'complain_record': complain_record
                # Pass the initial time_out value to the template
            })
        else:
            print("May error sa API PARE 33333")
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
        length = request.POST.get('length')
        
        length = int(length)
        
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
                current_time = datetime.now().time()

                if current_time > datetime.strptime("15:30:00", '%H:%M:%S').time():
                    # Compute the delay
                    delay_minutes = (datetime.combine(datetime.min, time_in) - datetime.combine(datetime.min, fstart_time)).seconds // 60
                    if delay_minutes > 0:
                        delay = f"{delay_minutes} minute{'s' if delay_minutes > 1 else ''} Late"
                    else:
                        delay = ''

                else:
                    delay = ''

            else:
                delay = ''
        else:
            return render(request, 'faculty_end/online_time_in.html', {'error_message': 'Failed to fetch data from the API'})

        # Status should be "Present" when time_in is logged
        status = 'Pending'

        # Set is_absent to False when status is Present
        is_absent = False

        if length != 0:
            has_attachments = True
        
        else:
            has_attachments = False


        # Save the data to the database
        online_record = Online.objects.create(
            user=request.user,
            day=day,
            time_in=time_in_str,
            time_start = fstart_time,
            time_out=time_out,
            room_name=room_name,
            date=date,
            month=month,
            delay=delay,
            status=status, 
            is_absent=is_absent, 
            has_attachments = has_attachments
        )

        online_record_id = online_record.id 
        if length != 0:

            for file_num in range(0, int(length)):
                print('File:', request.FILES.get(f'files{file_num}'))
                Evidence.objects.create(
                    online_id = online_record_id ,
                    uploaded_by = request.user,
                    name =  request.FILES.get(f'files{file_num}'), 
                    evidence = request.FILES.get(f'files{file_num}')
                    
                ) 

        # Redirect to the online_time_in view
        messages.success(request, 'Logged in successfully')
        # return redirect('faculty_attendance')  # Replace 'online_time_in' with the actual URL name of your view
        return JsonResponse({ 'success': True},status=200)
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
            
            initial_start_time_str = schedules_from_api[0].get('fstart_time', '') if schedules_from_api else ''
            if initial_start_time_str:
                initial_time_in = datetime.strptime(initial_start_time_str, '%H:%M:%S').strftime('%H:%M')
            else:
                initial_time_in = ''

            return render(request, 'faculty_end/online_time_in.html', {
                'schedules': processed_schedules,
                'current_day': current_day,
                'current_time': current_time,
                'current_date': current_date,
                'current_month': current_month,
                'initial_time_out': initial_time_out, 
                 'has_schedule': True, # Pass the initial time_out value to the template
                'initial_time_in': initial_time_in,  # Pass the initial time_out value to the template
            })
        else:
            return render(request, 'faculty_end/online_time_in.html', {'error_message': 'Failed to fetch data from the API', 'has_schedule': False})
        
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
    
    # Query TimeIn and Online based on start date
    if start_date:
        time_in_data = TimeIn.objects.filter(date__gte=start_date)
        online_data = Online.objects.filter(date__gte=start_date)
    else:
        time_in_data = TimeIn.objects.all()
        online_data = Online.objects.all()
    
    # Prepare attendance records including source information
    attendance_records = []

    for time_in_record in time_in_data:
        attendance_records.append({'record': time_in_record, 'type': 'Face-to-Face'})

    for online_record in online_data:
        attendance_records.append({'record': online_record, 'type': 'Online'})

    # Sort attendance records by created_at in descending order
    attendance_records.sort(key=lambda x: x['record'].created_at, reverse=True)

    context = {
        'attendance_records': attendance_records,
        'filter_option': filter_option,
    }
    return render(request, 'faculty_end/attendance_record.html', context)