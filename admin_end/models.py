#admin_end
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
    user_picture = models.ImageField(upload_to='user_pictures/', null=True)
    user_firstname = models.CharField(max_length=30)
    user_middlename = models.CharField(max_length=30, blank=True, null=True)
    user_lastname = models.CharField(max_length=30)
    extension_name = models.CharField(max_length=30, blank=True, null=True)
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
        return f"{self.user_firstname} {self.user_middlename} {self.user_lastname} {self.extension_name}"

class AcademicYear(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year_start = models.DateField()
    year_end = models.DateField()

class Semester(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester_name = models.CharField(max_length=100)

class FacultyShift(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    shift_day = models.CharField(max_length=20)  # Assuming you'll store the day as a string
    
class FacultyAccount(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    faculty_id = models.IntegerField(unique=True)

    
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
    approval_datetime = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.leave_application} - {self.decision}"
    
class AttendanceNotification(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.user_firstname} {self.user.user_lastname} - {self.date}"
    


