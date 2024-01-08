from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser, FacultyShift, Approval
from .forms import UserForm, ApprovalForm, FacultyShiftForm, UserUpdateForm
from django.db.models import OuterRef, Subquery
from django.views import View
from faculty_end.models import LeaveApplication, TimeIn, TimeOut
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test

def is_superadmin(user):
    return user.is_authenticated and user.is_superuser

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='admin').exists()

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def dashboard(request):
    return render(request,'admin_end/dashboard.html')

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def admin_notif(request):
    return render(request,'admin_end/admin_notif.html')

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = UserForm()
    
    return render(request, 'admin_end/user_create.html', {'form': form})

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_update(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            new_password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')

            if new_password and confirm_password and new_password == confirm_password:
                # Update password only if a new one is provided
                user.set_password(new_password)
                user.save(update_fields=['password'])

            user = form.save(commit=False)
            user.save(update_fields=['user_picture', 'user_firstname', 'user_lastname', 'user_role', 'email'])

            messages.success(request, 'User information updated successfully!')
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'admin_end/user_update.html', {'form': form, 'user': user})


@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_end/user_list.html', {'users': users})

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def user_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'admin_end/user_view.html', {'user': user})

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
            'schedule_display': schedule_display,
        })

    return render(request, 'admin_end/shift_list.html', {'faculty_schedule': faculty_schedule})

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_details(request, user_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')
    shifts = FacultyShift.objects.filter(user=faculty_user)
    return render(request, 'admin_end/shift_details.html', {'faculty_user': faculty_user, 'shifts': shifts})

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_create(request, user_id):
    faculty_user = get_object_or_404(CustomUser, id=user_id, user_role='faculty')

    if request.method == 'POST':
        form = FacultyShiftForm(request.POST)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.user = faculty_user
            shift.save()
            messages.success(request, 'Shift Created Successfully!')
            return redirect('shift_details', user_id=user_id)
    else:
        form = FacultyShiftForm()

    return render(request, 'admin_end/shift_create.html', {'faculty_user': faculty_user, 'form': form})

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

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def shift_delete(request, shift_id):
    print(f"Received shift_id: {shift_id}")
    shift = get_object_or_404(FacultyShift, id=shift_id)
    
    if request.method == 'POST':
        shift.delete()
        return redirect('shift_details', user_id=shift.user.id)

    return render(request, 'admin_end/shift_delete.html', {'shift': shift})

def login_as(request):
    return render(request,'admin_end/login_as.html')

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'Login Successfully.')
            return redirect('dashboard')  # Redirect to the shift list page after login
        else:
            messages.error(request, 'Invalid credentials or user is not a staff member.')
    return render(request, 'admin_end/admin_login.html')

@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('admin_login')

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'{user.user_firstname} {user.user_lastname} has been deactivated.')
    return redirect('user_list')

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'{user.user_firstname} {user.user_lastname} has been activated.')
    return redirect('user_list')

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def leaveappreq_list(request):
    leave_applications = LeaveApplication.objects.all()
    return render(request, 'admin_end/leaveappreq_list.html', {'leave_applications': leave_applications})

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def leaveappreq_view(request, leave_id):
    leave_application = LeaveApplication.objects.get(id=leave_id)
    return render(request, 'admin_end/leaveappreq_view.html', {'leave_application': leave_application})

@user_passes_test(is_superadmin, login_url='admin_login')
@login_required(login_url='admin_login')
def leaveappreq_decision(request, leave_id):
    leave_application = LeaveApplication.objects.get(id=leave_id)

    # Check if an associated Approval instance exists
    if not hasattr(leave_application, 'approval'):
        # If not, create a new Approval instance
        approval = Approval.objects.create(leave_application=leave_application)

    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            comment = form.cleaned_data['comment']
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
            approval.save()

            # Notify faculty about the decision
            # (You may want to implement a notification mechanism)

            messages.success(request, f'Leave application {decision}ed successfully.')
            return redirect('leaveappreq_list')
    else:
        form = ApprovalForm()

    return render(request, 'admin_end/leaveappreq_view.html', {'leave_application': leave_application, 'form': form})

def faculty_attendance_record(request):
    # Get all TimeIn and TimeOut records
    time_in_records = TimeIn.objects.all()
    time_out_records = TimeOut.objects.all()

    # Combine TimeIn and TimeOut records based on the user and date
    all_records = []
    for time_in_record in time_in_records:
        user = time_in_record.user
        date = time_in_record.date

        time_out_record = time_out_records.filter(user=user, date=date).first()

        all_records.append({
            'user': user,
            'date': date,
            'time_in': time_in_record.time_in,
            'time_in_status': time_in_record.status,
            'time_in_location': time_in_record.location,
            'time_out': time_out_record.time_out if time_out_record else None,
            'time_out_status': time_out_record.status if time_out_record else None,
            'time_out_location': time_out_record.location if time_out_record else None,
        })

    return render(request, 'admin_end/faculty_attendance_record.html', {'all_records': all_records})