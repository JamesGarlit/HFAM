# faculty_end/management/commands/create_dummy_time_entries.py
from django.core.management.base import BaseCommand
from faker import Faker
from admin_end.models import CustomUser, FacultyShift
from faculty_end.models import TimeIn, TimeOut

fake = Faker()

class Command(BaseCommand):
    help = 'Create dummy data for time in and time out for existing dummy users.'

    def handle(self, *args, **options):
        # Fetch existing users with IDs from 2 to 100
        existing_users = CustomUser.objects.filter(id__range=(2, 100))

        # Your dummy data creation logic here for time in and time out
        for user in existing_users:
            # Fetch shifts for the user
            shifts = FacultyShift.objects.filter(user=user)

            for shift in shifts:
                for _ in range(5):  # Create 5 dummy time in and time out entries for each user
                    location = fake.company()
                    date = fake.date_between(start_date='-30d', end_date='today')

                    # Create dummy time in entry
                    TimeIn.objects.create(
                        user=user,
                        faculty_shift=shift,
                        location=location,
                        date=date,
                        time_in=fake.time(),
                        status=fake.random_element(elements=('On Time', 'Late', 'Early', 'Absent')),
                    )

                    # Create dummy time out entry
                    TimeOut.objects.create(
                        user=user,
                        faculty_shift=shift,
                        location=location,
                        date=date,
                        time_out=fake.time(),
                        status=fake.random_element(elements=('On Time', 'Late', 'Early', 'Absent')),
                    )

                    self.stdout.write(self.style.SUCCESS(f'Successfully created time in and time out entries for user: {user.email}'))
