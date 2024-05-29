# admin_end/urls.py
from django.urls import path

from faculty_end.views_absent import check_attendance
from .views import update_status, overall, directordashboard, user_attendance_view, approve_attendance, disapprove_attendance, online_approval, complaints_f2f, supmerged_table, supdashboard, suppresent_users_chart, supabsent_users_chart, onlineqrcode, generate_qr, dashboard, present_users_chart, absent_users_chart, dashboard, merged_table, update_faculty_account, create_faculty_account, admin_settings, schedule_api, user_create, user_list, faculty_members, user_update, user_view, login, login_as, admin_logout, deactivate_user, activate_user
from .views_reports import DTRReport
from .views_validation import approved, approved_revalidation, rejected, rejected_revalidation

urlpatterns = [
    path('online_approval/', user_attendance_view, name='user_attendance'),
    path('online_approval/approve/<int:online_id>/', approve_attendance, name='approve_attendance'),
    path('online_approval/disapprove/<int:online_id>/', disapprove_attendance, name='disapprove_attendance'),
    path('user_create/', user_create, name='user_create'),
    path('generate_qr/', generate_qr, name='generate_qr'),
    path('complaints_f2f/', complaints_f2f, name='complaints_f2f'),
    path('onlineqrcode/', onlineqrcode, name='onlineqrcode'),
    path('user_list/', user_list, name='user_list'),
    path('faculty_members/', faculty_members, name='faculty_members'),
    path('create_faculty_account/<int:faculty_id>/', create_faculty_account, name='create_faculty_account'),
    path('update_faculty_account/<int:faculty_id>/', update_faculty_account, name='update_faculty_account'),
    path('user_update/<int:user_id>/', user_update, name='user_update'),
    path('user_view/<int:user_id>/', user_view, name='user_view'),
    path('login/', login, name='login'),
    path('', login_as, name='login_as'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('user_deactivate/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('user_activate/<int:user_id>/', activate_user, name='activate_user'),
    path('schedule_api/', schedule_api, name='schedule_api'),
    path('admin_settings/', admin_settings, name='admin_settings'),
    path('merged_table/', merged_table, name='merged_table'),
    path('supmerged_table/', supmerged_table, name='supmerged_table'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/present_users_chart-chart/', present_users_chart, name='present_users_chart'),
    path('dashboard/absent-users-chart/', absent_users_chart, name='absent_users_chart'),
    path('supdashboard/', supdashboard, name='supdashboard'),
    path('supdashboard/present_users_chart-chart/', suppresent_users_chart, name='supsuppresent_users_chart'),
    path('supdashboard/absent-users-chart/', supabsent_users_chart, name='supabsent_users_chart'),
    path('online_approval/', online_approval, name='online_approval'),
    path('update_status/', update_status, name='update_status'),

    path('overall/', overall, name='overall'),
    
    path('directordashboard/', directordashboard, name='directordashboard'),

    # These are the paths for all the reports
    path('reports/dtr/', DTRReport, name='report-dtr'),

    # AUTOMATION URLS
    path('automate/time-in/absent/', check_attendance, name='check-attendance'),

    path('validate/approved/', approved, name='validate-approved'),
    path('validate/rejected/', rejected, name='validate-rejected'),

    path('revalidate/approved/<int:onsite_id>/', approved_revalidation, name='revalidate-approved'),
    path('revalidate/rejected/<int:onsite_id>/', rejected_revalidation, name='revalidate-rejected'),
]
