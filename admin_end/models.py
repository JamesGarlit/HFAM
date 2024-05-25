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
        if extra_fields.get('user_role') in ['admin', 'superadmin', 'Academic Head']:
            extra_fields.setdefault('is_superuser', True)
        else:
            extra_fields.setdefault('is_superuser', False)
        print("Creating superuser with extra_fields:", extra_fields)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_picture = models.ImageField(upload_to='user_pictures/')
    user_firstname = models.CharField(max_length=30)
    user_middlename = models.CharField(max_length=30, blank=True)
    user_lastname = models.CharField(max_length=30)
    extension_name = models.CharField(max_length=30, blank=True)
    employment_status = models.CharField(max_length=10)
    user_role = models.CharField(max_length=20)
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
        if self.user_role in ['admin', 'superadmin', 'Academic Head']:
            self.is_superuser = True
        super().save(*args, **kwargs)

    def get_full_name(self):
        full_name = f"{self.user_firstname}"
        if self.user_middlename:
            full_name += f" {self.user_middlename}"
        full_name += f" {self.user_lastname}"
        if self.extension_name:
            full_name += f" {self.extension_name}"
        return full_name

class FacultyAccount(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    faculty_id = models.IntegerField(unique=True)

class AcademicYear(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    year_start = models.IntegerField()
    year_end = models.IntegerField()

class Semester(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester_name = models.CharField(max_length=100)


    

    


