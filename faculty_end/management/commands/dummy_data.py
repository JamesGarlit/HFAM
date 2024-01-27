from django.core.management.base import BaseCommand
from faker import Faker
from admin_end.models import CustomUser, FacultyShift
from faculty_end.models import TimeIn, TimeOut
from datetime import timedelta

fake = Faker()

class Command(BaseCommand):
    help = 'Create dummy data'

    def handle(self, *args, **options):
        existing_faculty_users = CustomUser.objects.filter(user_role='faculty')
        faculty_shifts = FacultyShift.objects.all()

        for user in existing_faculty_users:
            for _ in range(fake.random_int(min=1, max=5)):
                date = fake.date_between(start_date='-30d', end_date='today') + timedelta(days=fake.random_int(min=1, max=5))
                time_in_status = fake.random_element(elements=('On Time', 'Late', 'Early', 'Absent'))
                time_out_status = 'Absent' if time_in_status == 'Absent' else fake.random_element(elements=('On Time', 'Late', 'Early', 'Absent'))

                faculty_shift_instance = fake.random_element(elements=faculty_shifts)

                TimeIn.objects.create(
                    user=user,
                    faculty_shift=faculty_shift_instance,
                    location=fake.city(),
                    date=date,
                    time_in=fake.time(),
                    status=time_in_status
                )

                TimeOut.objects.create(
                    user=user,
                    faculty_shift=faculty_shift_instance,
                    location=fake.city(),
                    date=date,
                    time_out=fake.time(),
                    status=time_out_status
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created TimeIn and TimeOut for faculty user: {user.email}'))
