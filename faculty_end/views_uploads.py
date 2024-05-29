# faculty_end/views.py
from django.contrib import messages
from .models import Complains, Online, Evidence, TimeIn
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

            complains_exist = Complains.objects.filter(onsite_id=onsite_id).exists()

            if complains_exist == False:
 
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

            else:
                complains_record = Complains.objects.get(onsite_id=onsite_id)
                complains_record.complains = complains
                complains_record.validated_by = None
                complains_record.validated_at = None

                complains_id = complains_record.id

                complains_record.save()

                queryset = Evidence.objects.filter(complain_id=complains_id)
                queryset.delete()

                for file_num in range(0, int(length)):
                    print('File:', request.FILES.get(f'files{file_num}'))
                    Evidence.objects.create(
                        complain_id = complains_id ,
                        uploaded_by = request.user,
                        name =  request.FILES.get(f'files{file_num}'), 
                        evidence = request.FILES.get(f'files{file_num}')
                        
                    ) 

            onsite_record = TimeIn.objects.get(id=onsite_id)
            onsite_record.justification_count = onsite_record.justification_count + 1
            onsite_record.acadhead_is_responded = False
            onsite_record.submitted_complaint = True
            onsite_record.validation_comment = None
            onsite_record.save()

            # Provide a success message as a JSON response
            messages.success(request, f'Justification successfully submitted!') 
            return JsonResponse({"status": "success"}, status=200)
        else:
            return JsonResponse({'error': 'Please attach a file before submitting the form.'}, status=400)
        


    else:
        # Return a validation error as a JSON response
        return JsonResponse({'error': 'Invalid request method.'}, status=400)