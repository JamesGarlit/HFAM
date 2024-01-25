# your_app/management/commands/create_dummy_users.py
from django.core.management.base import BaseCommand
from admin_end.factories import CustomUserFactory

class Command(BaseCommand):
    help = 'Create dummy users for testing purposes.'

    def handle(self, *args, **options):
        # Your dummy data creation logic here
        for _ in range(200):
            CustomUserFactory.create()
        self.stdout.write(self.style.SUCCESS('Successfully created dummy users.'))
