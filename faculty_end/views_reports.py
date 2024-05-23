# faculty_end/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LeaveApplication, TimeIn, TimeOut
from django.contrib.auth import authenticate, login, logout
from admin_end.models import FacultyShift, CustomUser, LeaveApplicationAction
from datetime import datetime, timedelta
from django.contrib.auth import update_session_auth_hash
import requests
from django.utils import timezone

