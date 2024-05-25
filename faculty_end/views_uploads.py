# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Complains, LeaveApplication, Online, Evidence, TimeIn, TimeOut
from django.contrib.auth import authenticate, login, logout
from admin_end.models import CustomUser
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
import requests
from django.utils import timezone
from datetime import date
from django.http import JsonResponse

def upload_evidence(request, pk):
    # Retrieve the type object with the given primary key (pk)
    try:
        online_record = Online.objects.get(id=pk)
    except Online.DoesNotExist:
        return JsonResponse({'error': 'Online Record not found'}, status=404)


    # update_form = Create_Bodies_Form(instance=type)
    if request.method == 'POST':
        length = request.POST.get('length')
        is_red_instruction = request.POST.get('user_approval')
        print('USER APPROVAL: ', is_red_instruction)
        length = int(length)
        if length != 0:
            online_record.is_red_instruction =  is_red_instruction
            online_record.has_attachments =  True
            online_record.save()

            for file_num in range(0, int(length)):
                print('File:', request.FILES.get(f'files{file_num}'))
                Evidence.objects.create(
                    online_id = int(pk) ,
                    uploaded_by = request.user,
                    name =  request.FILES.get(f'files{file_num}'), 
                    evidence = request.FILES.get(f'files{file_num}')
                    
                ) 
            # Provide a success message as a JSON response
            messages.success(request, f'The Evidences successfully uploaded!') 
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({'error': 'Please attach a file before submitting the form.'}, status=400)
        


    else:
        # Return a validation error as a JSON response
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    


def submit_complaint(request):
    # update_form = Create_Bodies_Form(instance=type)
    if request.method == 'POST':
        length = request.POST.get('length')
        complains = request.POST.get('complains')
        user_id = request.user.id
        onsite_id =  request.POST.get('onsite_id')

        length = int(length)
        if length != 0:
 
            complain_record = Complains.objects.create(
                onsite_id = onsite_id,
                complainant_id = user_id,
                complains = complains
            )

            complaint_id = complain_record.id


            for file_num in range(0, int(length)):
                print('File:', request.FILES.get(f'files{file_num}'))
                Evidence.objects.create(
                    complain_id = complaint_id ,
                    uploaded_by = request.user,
                    name =  request.FILES.get(f'files{file_num}'), 
                    evidence = request.FILES.get(f'files{file_num}')
                    
                ) 
            # Provide a success message as a JSON response
            messages.success(request, f'The Evidences successfully uploaded!') 
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({'error': 'Please attach a file before submitting the form.'}, status=400)
        


    else:
        # Return a validation error as a JSON response
        return JsonResponse({'error': 'Invalid request method.'}, status=400)