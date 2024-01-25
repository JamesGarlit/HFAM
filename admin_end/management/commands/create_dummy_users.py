# admin_end/management/commands/create_dummy_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
from admin_end.models import CustomUser, FacultyShift

fake = Faker()

class Command(BaseCommand):
    help = 'Create shifts for existing dummy users for testing purposes.'

    def handle(self, *args, **options):
        # Fetch existing users with IDs from 2 to 100
        existing_users = CustomUser.objects.filter(id__range=(2, 100))

        # Your dummy data creation logic here for shifts
        for user in existing_users:
            FacultyShift.objects.create(
                user=user,
                shift_start=fake.time(),
                shift_end=fake.time(),
                shift_day=fake.random_element(elements=('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created shift for user: {user.email}'))
