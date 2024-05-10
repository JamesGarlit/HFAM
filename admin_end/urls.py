# admin_end/urls.py
from django.urls import path
from .views import accepted_leaveapp, update_faculty_account, create_faculty_account, admin_settings, schedule_api, absenteeism_analysis, user_create, user_list, faculty_members, user_update, user_view, shift_list, shift_list, shift_details, shift_create, shift_update, shift_delete, login, login_as, admin_logout, dashboard, deactivate_user, activate_user, admin_notif, leaveappreq_list, approval, faculty_attendance_record, attendance_notif


urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('admin_notif/', admin_notif, name='admin_notif'),
    path('user_create/', user_create, name='user_create'),
    path('user_list/', user_list, name='user_list'),
    path('faculty_members/', faculty_members, name='faculty_members'),
    path('create_faculty_account/<int:faculty_id>/', create_faculty_account, name='create_faculty_account'),
    path('update_faculty_account/<int:faculty_id>/', update_faculty_account, name='update_faculty_account'),
    path('user_update/<int:user_id>/', user_update, name='user_update'),
    path('user_view/<int:user_id>/', user_view, name='user_view'),
    path('shift_list/', shift_list, name='shift_list'),
    path('shift_details/<int:user_id>/', shift_details, name='shift_details'),
    path('shift_create/<int:user_id>/', shift_create, name='shift_create'),
    # path('shift_update/<int:shift_id>/', shift_update, name='shift_update'),
    path('shift_update/<int:user_id>/<int:shift_id>/', shift_update, name='shift_update'),
    path('shift_delete/<int:shift_id>/', shift_delete, name='shift_delete'),
    path('login/', login, name='login'),
    path('', login_as, name='login_as'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('user_deactivate/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('user_activate/<int:user_id>/', activate_user, name='activate_user'),
    path('leaveappreq_list/', leaveappreq_list, name='leaveappreq_list'),
    path('leaveappreq_list/', accepted_leaveapp, name='accepted_leaveapp'),
    path('approval/<int:leave_app_id>/', approval, name='approval'),
    path('faculty_attendance_record/', faculty_attendance_record, name='faculty_attendance_record'),
    path('attendance_notif/', attendance_notif, name='attendance_notif'),
    path('dashboard/', absenteeism_analysis, name='absenteeism_analysis'),
    path('schedule_api/', schedule_api, name='schedule_api'),
    path('admin_settings/', admin_settings, name='admin_settings'),
    

]
