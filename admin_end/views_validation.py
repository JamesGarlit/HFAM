from django.shortcuts import redirect
from django.contrib import messages
from faculty_end.models import Complains, TimeIn, Online
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
import requests

def approved(request):
    if request.method == 'POST':
        comments = request.POST.get('comment')
        record_id = request.POST.get('record_id')

        try:
            record = TimeIn.objects.get(id=record_id)

            record.is_approved = True
            record.status = "Present"
            record.validation_comment = f"Approved by {comments}"
            record.checker_created_at = timezone.now()
            record.save()

            messages.success(request, f'The record is validated successfully!') 
            return JsonResponse({'success': True}, status=200)

        except TimeIn.DoesNotExist:

            try:
                record = Online.objects.get(id=record_id)
                record.is_approved = True
                record.validation_comment = comments
                record.status = "Present"
                record.save()
                messages.success(request, f'The record is validated successfully!') 
                return JsonResponse({'success': True}, status=200)
            
            except Online.DoesNotExist:
                return JsonResponse({'error': 'There is no available record. Please try again.'}, status=404)
    else:
        # Return a validation error using a JSON response
        return JsonResponse({'error': 'Invalid request. Please try again.'}, status=400)




def rejected(request):
    if request.method == 'POST':
        comments = request.POST.get('comment')
        record_id = request.POST.get('record_id')


        try:
            record = TimeIn.objects.get(id=record_id)
            record.status = "Absent"
            record.is_approved = False
            record.is_absent = True
            record.validation_comment = f"Invalidated by {comments}"
            record.checker_created_at = timezone.now()
            record.save()

            messages.success(request, f'The record is validated successfully!') 
            return JsonResponse({'success': True}, status=200)

        except TimeIn.DoesNotExist:

            try:
                record = Online.objects.get(id=record_id)
                record.is_approved = False
                record.validation_comment = comments
                record.status = "Absent"
                record.is_absent = True
                record.save()
                messages.success(request, f'The record is validated successfully!') 
                return JsonResponse({'success': True}, status=200)
            
            except Online.DoesNotExist:
                return JsonResponse({'error': 'There is no available record. Please try again.'}, status=404)
    else:
        # Return a validation error using a JSON response
        return JsonResponse({'error': 'Invalid request. Please try again.'}, status=400)
    


def approved_revalidation(request, onsite_id):
    if request.method == 'POST':
        record = TimeIn.objects.get(id=onsite_id)
        record.status = "Present"
        record.is_absent = False
        record.acadhead_created_at = timezone.now()
        record.validation_comment = f"Approved by Demelyn Monzon {request.user.get_full_name()}"
        record.acadhead_is_responded = True
        record.save()


        complain = Complains.objects.get(onsite_id=onsite_id)
        complain.is_resolved = True
        complain.validated_by = request.user
        complain.validated_at = timezone.now()
        complain.save()
        messages.success(request, f'The record is revalidated successfully!') 
        # return JsonResponse({'success': True}, status=200)
        return redirect('complaints_f2f')
    
                
    else:
        # Return a validation error using a JSON response
        return JsonResponse({'error': 'Invalid request. Please try again.'}, status=400)




def rejected_revalidation(request, onsite_id):
    if request.method == 'POST':
        reason = request.POST.get('reason')

        record = TimeIn.objects.get(id=onsite_id)
        record.is_absent = True
        record.status = "Absent"
        record.acadhead_created_at = timezone.now()
        record.validation_comment = f"Invalidated by Demelyn Monzon : {reason}"
        record.acadhead_is_responded = True
        record.save()


        complain = Complains.objects.get(onsite_id=onsite_id)
        complain.is_resolved = False
        complain.validated_by = request.user
        complain.validated_at = timezone.now()
        complain.save()
        messages.success(request, f'The record is revalidated successfully!') 
        return redirect('complaints_f2f')
        # return JsonResponse({'success': True}, status=200)
    
                
    else:
        # Return a validation error using a JSON response
        return JsonResponse({'error': 'Invalid request. Please try again.'}, status=400)
    


def online_approved_revalidation(request, online_id):
    if request.method == 'POST':
        record = Online.objects.get(id=online_id)
        record.status = "Present"
        record.is_absent = False
        record.acadhead_created_at = timezone.now()
        record.validation_comment = f"Revalidated by {request.user.get_full_name()}"
        record.acadhead_is_responded = True
        record.save()


        complain = Complains.objects.get(online_id=online_id)
        complain.is_resolved = True
        complain.validated_by = request.user
        complain.validated_at = timezone.now()
        complain.save()
        messages.success(request, f'The record is revalidated successfully!') 
        # return JsonResponse({'success': True}, status=200)
        return redirect('complaints_online')
    
                
    else:
        # Return a validation error using a JSON response
        return JsonResponse({'error': 'Invalid request. Please try again.'}, status=400)




def online_rejected_revalidation(request, online_id):
    if request.method == 'POST':
        reason = request.POST.get('reason')

        record = Online.objects.get(id=online_id)
        record.is_absent = True
        record.status = "Absent"
        record.acadhead_created_at = timezone.now()
        record.validation_comment = f"Acad Head remarks: {reason}"
        record.acadhead_is_responded = True
        record.save()


        complain = Complains.objects.get(online_id=online_id)
        complain.is_resolved = False
        complain.validated_by = request.user
        complain.validated_at = timezone.now()
        complain.save()
        messages.success(request, f'The record is revalidated successfully!') 
        return redirect('complaints_online')
        # return JsonResponse({'success': True}, status=200)
    
                
    else:
        # Return a validation error using a JSON response
        return JsonResponse({'error': 'Invalid request. Please try again.'}, status=400)