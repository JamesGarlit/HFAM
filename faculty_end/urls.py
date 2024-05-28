from django.urls import path

from faculty_end.views_uploads import submit_complaint, upload_evidence
from .views import error_message, log_attendance, online_time_in, faculty_attendance, log_time_in, log_time_out, faculty_login, faculty_logout, qrcode_generator, faculty_login, account_settings, change_password, error_400

urlpatterns = [ 
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('faculty_logout/', faculty_logout, name='faculty_logout'),
    path('qrcode_generator/', qrcode_generator, name='qrcode_generator'),
    path('faculty_login/', faculty_login, name='faculty_login'),
    path('log_attendance/', log_attendance, name='log_attendance'),
    path('error_message/', error_message, name='error_message'),
    path('account_settings/', account_settings, name='account_settings'),
    path('change_password/', change_password, name='change_password'),
    path('error_400/', error_400, name='error_400'),
    path('log_time_in/', log_time_in, name='log_time_in'),
    path('online_time_in/', online_time_in, name='online_time_in'),
    path('log_time_out/', log_time_out, name='log_time_out'),
    path('faculty_attendance/', faculty_attendance, name='faculty_attendance'),

    path('upload/evidence/<str:pk>/', upload_evidence, name='upload-evidence'),

    path('submit/complaint/', submit_complaint, name='submit-complaint'),

]