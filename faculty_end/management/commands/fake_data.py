from django.core.management.base import BaseCommand
from django.utils import timezone
from admin_end.models import CustomUser  # Import CustomUser model from admin_end app
from faculty_end.models import TimeIn, TimeOut
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generate fake data for TimeIn and TimeOut'

    def handle(self, *args, **options):
        fake = Faker()
        user_email = "soberano123@gmail.com"  # User's email for whom fake data will be generated

        # Retrieve the user or create one if it doesn't exist
        user, created = CustomUser.objects.get_or_create(email=user_email, defaults={
            'user_firstname': fake.first_name(),
            'user_lastname': fake.last_name(),
            'user_role': 'faculty',  # Assuming a default role for the user
        })

        # Generate fake data for TimeIn
        for _ in range(10):
            TimeIn.objects.create(
                user=user,
                location=fake.address(),
                date=fake.date_between(start_date='-1y', end_date='today'),
                time_in=fake.time(pattern='%H:%M:%S', end_datetime=timezone.now()),
                status=random.choice(['Early', 'Late', 'On Time']),
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )

        # Generate fake data for TimeOut
        for _ in range(10):
            TimeOut.objects.create(
                user=user,
                location=fake.address(),
                date=fake.date_between(start_date='-1y', end_date='today'),
                time_out=fake.time(pattern='%H:%M:%S', end_datetime=timezone.now()),
                status=random.choice(['Early', 'Late', 'On Time']),
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )

        self.stdout.write(self.style.SUCCESS('Fake data generated successfully.'))
