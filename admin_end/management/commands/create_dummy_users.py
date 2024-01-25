# admin_end/management/commands/create_dummy_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
from admin_end.models import CustomUser

fake = Faker()

class Command(BaseCommand):
    help = 'Create dummy users for testing purposes.'

    def handle(self, *args, **options):
        # Your dummy data creation logic here
        for _ in range(200):  # Create 200 dummy users
            user_created_by_manager = CustomUser.objects.create_user(
                email=fake.email(),
                password=make_password(fake.password()),  # Hash the password
                user_firstname=fake.first_name(),
                user_middlename=fake.first_name(),
                user_lastname=fake.last_name(),
                extension_name=fake.suffix(),
                employment_status=fake.random_element(elements=('Full-Time', 'Part-Time')),
                user_role=fake.random_element(elements=('admin', 'faculty', 'superadmin')),
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created dummy user: {user_created_by_manager.email}'))
