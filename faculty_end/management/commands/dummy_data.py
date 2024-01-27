from django.core.management.base import BaseCommand
from faker import Faker
from admin_end.models import CustomUser, FacultyShift
from faculty_end.models import TimeIn, TimeOut
from datetime import timedelta

fake = Faker()

from datetime import timedelta

class Command(BaseCommand):
    help = 'Create dummy data'

    def handle(self, *args, **options):
        existing_faculty_users = CustomUser.objects.filter(user_role='faculty')

        for user in existing_faculty_users:
            for _ in range(fake.random_int(min=1, max=5)):  # Add 1 to 5 days of data
                date = fake.date_between(start_date='-30d', end_date='today') + timedelta(days=fake.random_int(min=1, max=5))
                time_in_status = fake.random_element(elements=('On Time', 'Late', 'Early', 'Absent'))
                time_out_status = 'Absent' if time_in_status == 'Absent' else fake.random_element(elements=('On Time', 'Late', 'Early', 'Absent'))

                TimeIn.objects.create(
                    user=user,
                    faculty_shift=FacultyShift.objects.get(id=1),
                    location=fake.city(),
                    date=date,
                    time_in=fake.time(),
                    status=time_in_status
                )

                TimeOut.objects.create(
                    user=user,
                    faculty_shift=FacultyShift.objects.get(id=1),
                    location=fake.city(),
                    date=date,
                    time_out=fake.time(),
                    status=time_out_status
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created TimeIn and TimeOut for faculty user: {user.email}'))

