# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TimeIn, TimeOut
from django.contrib.auth import authenticate, login, logout
from admin_end.models import CustomUser
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
import requests
from django.utils import timezone
from datetime import date
from django.http import HttpResponse, JsonResponse

def check_attendance(request):
    # Get faculty ID and current day
    faculty_id = request.user.facultyaccount.faculty_id
    current_day = datetime.now().strftime('%A')

    # Fetch data from the Scheduler API
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

            room_name = schedule_info.get('roomname', '')

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


        if schedules_from_api:
            # Check if the user already timed in
            
            is_TimedIn = TimeIn.objects.filter(user=request.user, date=date.today()).exists()
        
            # If the user already timed in, just pass a success code
            if is_TimedIn:
                return JsonResponse({'success0': True}, status=200)
            
            else:
                # If the user still didn't timed in, it will check if the end time of the schedule had passed. If so, it will mark it as absent
                if current_time > initial_time_out:
                    # Save the data to the database

                    TimeIn.objects.create(
                        user = request.user,
                        day=current_day,
                        time_in= None,
                        time_out= None,
                        room_name=room_name,
                        date=current_date,
                        month=current_month,
                        status = 'Absent',
                        is_absent = True
                    )

                    return JsonResponse({'success1': True}, status=200)
                
                else:
                    return JsonResponse({'success2': True}, status=200)
                
        else:
            return JsonResponse({'success3': True}, status=200)