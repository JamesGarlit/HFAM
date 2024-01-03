from django.urls import path
from .views import leaveapp_create, leaveapp_list, leaveapp_view, faculty_login, faculty_logout, qrcode_scanner, qrcode_generator, faculty_login, attendance_record, time_in, time_out

urlpatterns = [
    path('leaveapp_create/', leaveapp_create, name='leaveapp_create'),
    path('leaveapp_list/', leaveapp_list, name='leaveapp_list'),
    path('leaveapp_view<int:leave_id>/', leaveapp_view, name='leaveapp_view'),
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('faculty_logout/', faculty_logout, name='faculty_logout'),
    path('qrcode_scanner/', qrcode_scanner, name='qrcode_scanner'),
    path('qrcode_generator/', qrcode_generator, name='qrcode_generator'),
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('attendance_record/', attendance_record, name='attendance_record'),
    path('time_in/', time_in, name='time_in'),
    path('time_out/', time_out, name='time_out'),
]