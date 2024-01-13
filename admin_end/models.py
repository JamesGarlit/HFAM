# admin_end/models.py
# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
# from django.contrib.auth import get_user_model

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(email, password, **extra_fields)
    
# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     user_picture = models.ImageField(upload_to='user_pictures/', null=True, blank=True)
#     user_firstname = models.CharField(max_length=30)
#     user_lastname = models.CharField(max_length=30)
#     employment_status = models.CharField(max_length=10)
#     user_role = models.CharField(max_length=10)
#     email = models.EmailField(unique=True)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=True)

#     groups = models.ManyToManyField(Group, blank=True, related_name='customuser_set', related_query_name='user')
#     user_permissions = models.ManyToManyField(Permission, blank=True, related_name='customuser_set', related_query_name='user')

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['user_firstname', 'user_lastname', 'user_role']
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.contrib.auth import get_user_model

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('user_role') in ['admin', 'superadmin']:
            extra_fields.setdefault('is_superuser', True)
        else:
            extra_fields.setdefault('is_superuser', False)
        print("Creating superuser with extra_fields:", extra_fields)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_picture = models.ImageField(upload_to='user_pictures/', null=True, blank=True)
    user_firstname = models.CharField(max_length=30)
    user_lastname = models.CharField(max_length=30)
    employment_status = models.CharField(max_length=10)
    user_role = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    groups = models.ManyToManyField(Group, blank=True, related_name='customuser_set', related_query_name='user')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='customuser_set', related_query_name='user')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_firstname', 'user_lastname', 'user_role']

    def save(self, *args, **kwargs):
        # Check if is_superuser should be set based on user_role
        if self.user_role in ['admin', 'superadmin']:
            self.is_superuser = True
        super().save(*args, **kwargs)


    def get_full_name(self):
        return f"{self.user_firstname} {self.user_lastname}"
    
class FacultyShift(models.Model):
    SHIFT_DAYS = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='faculty_shifts')
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    shift_day = models.CharField(max_length=10, choices=SHIFT_DAYS)

    def get_schedule_display(self):
        # Format the time in 12-hour format with AM/PM
        start_time = self.shift_start.strftime('%I:%M %p')
        end_time = self.shift_end.strftime('%I:%M %p')

        # Combine the formatted time with other schedule details
        return f"{self.shift_day}: {start_time} - {end_time}"

    
class Approval(models.Model):
    DECISION_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    leave_application = models.OneToOneField('faculty_end.LeaveApplication', on_delete=models.CASCADE)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES, default='pending')
    comment = models.CharField(max_length=250, blank=True, null=True)
    admin_user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    approval_datetime = models.DateTimeField(default='2024-01-10 18:27:59')  # This field will store the approval date and time

    def __str__(self):
        return f"{self.leave_application} - {self.decision}"
