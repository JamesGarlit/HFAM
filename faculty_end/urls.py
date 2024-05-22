from django.urls import path
from .views import log_attendance, online_time_in, attendance_record, log_time_in, log_time_out, time_in_out_records, leaveapp_create, leaveapp_list, leaveapp_view, faculty_login, faculty_logout, qrcode_generator, faculty_login, attendance_record1, notif, account_settings, change_password, error_400

urlpatterns = [
    path('leaveapp_create/', leaveapp_create, name='leaveapp_create'),
    path('leaveapp_list/', leaveapp_list, name='leaveapp_list'),
    # path('leaveapp_view<int:leave_id>/', leaveapp_view, name='leaveapp_view'),
    path('leaveapp_view/<int:leave_app_id>/', leaveapp_view, name='leaveapp_view'),  
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('faculty_logout/', faculty_logout, name='faculty_logout'),
    path('qrcode_generator/', qrcode_generator, name='qrcode_generator'),
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('log_attendance/', log_attendance, name='log_attendance'),
    path('attendance_record1/', attendance_record1, name='attendance_record1'),
    path('notif/', notif, name='notif'),
    path('account_settings/', account_settings, name='account_settings'),
    path('change_password/', change_password, name='change_password'),
    path('error_400/', error_400, name='error_400'),
    path('attendance_record/<int:faculty_shift_id>/', time_in_out_records, name='time_in_out_records'),
    path('log_time_in/', log_time_in, name='log_time_in'),
    path('online_time_in/', online_time_in, name='online_time_in'),
    path('log_time_out/', log_time_out, name='log_time_out'),
    path('attendance_record/', attendance_record, name='attendance_record'),


]