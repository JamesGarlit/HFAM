# admin_end/urls.py
from django.urls import path
from . import views
from .views import user_create, user_list, user_list_api, user_update, user_view, shift_list, shift_list, shift_details, shift_create, shift_update, shift_delete, admin_login, login_as, admin_logout, dashboard, deactivate_user, activate_user, admin_notif, leaveappreq_decision, leaveappreq_list, leaveappreq_view, faculty_attendance_record, attendance_notif


urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('admin_notif/', admin_notif, name='admin_notif'),
    path('user_create/', user_create, name='user_create'),
    path('user_list/', user_list, name='user_list'),
    path('user_list_api/', user_list_api, name='user_list_api'),
    path('user_update/<int:user_id>/', user_update, name='user_update'),
    path('user_view/<int:user_id>/', user_view, name='user_view'),
    path('shift_list/', shift_list, name='shift_list'),
    path('shift_details/<int:user_id>/', shift_details, name='shift_details'),
    path('shift_create/<int:user_id>/', shift_create, name='shift_create'),
    path('shift_update/<int:shift_id>/', shift_update, name='shift_update'),
    path('shift_delete/<int:shift_id>/', shift_delete, name='shift_delete'),
    path('admin_login/', admin_login, name='admin_login'),
    path('', login_as, name='login_as'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('user_deactivate/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('user_activate/<int:user_id>/', activate_user, name='activate_user'),
    path('leaveappreq_list/', leaveappreq_list, name='leaveappreq_list'),
    path('leaveappreq_view/<int:leave_id>/', leaveappreq_view, name='leaveappreq_view'),
    path('leaveappreq_decision/<int:leave_id>/', leaveappreq_decision, name='leaveappreq_decision'),
    path('faculty_attendance_record/', faculty_attendance_record, name='faculty_attendance_record'),
    path('attendance_notif/', attendance_notif, name='attendance_notif'),
]
