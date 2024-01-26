# faculty_end/management/commands/dummy_data.py
from django.core.management.base import BaseCommand
from faker import Faker
from admin_end.models import CustomUser, FacultyShift
from faculty_end.models import LeaveApplication

fake = Faker()

class Command(BaseCommand):
    help = 'Create dummy data'

    def handle(self, *args, **options):
        # Fetch existing users with faculty role
        existing_faculty_users = CustomUser.objects.filter(user_role='faculty')

        # Your dummy data creation logic here for leave applications
        for user in existing_faculty_users:
            for _ in range(2):  # Create 2 dummy leave applications for each faculty user
                leave_start_date = fake.date_between(start_date='-30d', end_date='today')
                leave_start_time = fake.time()
                leave_end_date = fake.date_between(start_date=leave_start_date, end_date=leave_start_date.replace(year=leave_start_date.year + 1))
                leave_end_time = fake.time()
                leave_type = fake.random_element(elements=('Sick Leave', 'Vacation', 'Personal Leave'))
                leave_reason = fake.text()

                LeaveApplication.objects.create(
                    user=user,
                    leave_start_date=leave_start_date,
                    leave_start_time=leave_start_time,
                    leave_end_date=leave_end_date,
                    leave_end_time=leave_end_time,
                    leave_type=leave_type,
                    leave_reason=leave_reason,
                    leave_datetime_submitted=fake.date_time_this_decade(),
                    is_viewed=False
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created leave application for faculty user: {user.email}'))
