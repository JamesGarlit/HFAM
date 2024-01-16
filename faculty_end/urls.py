from django.urls import path
from .views import leaveapp_create, leaveapp_list, leaveapp_view, faculty_login, faculty_logout, qrcode_generator, faculty_login, time_in, time_out, attendance_record, notif


urlpatterns = [
    path('leaveapp_create/', leaveapp_create, name='leaveapp_create'),
    path('leaveapp_list/', leaveapp_list, name='leaveapp_list'),
    path('leaveapp_view<int:leave_id>/', leaveapp_view, name='leaveapp_view'),
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('faculty_logout/', faculty_logout, name='faculty_logout'),
    path('qrcode_generator/', qrcode_generator, name='qrcode_generator'),
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('attendance_record/', attendance_record, name='attendance_record'),
    path('time_in/<int:faculty_shift_id>/', time_in, name='time_in'),
    path('time_out/<int:faculty_shift_id>/', time_out, name='time_out'),
    path('notif/', notif, name='notif'),
]