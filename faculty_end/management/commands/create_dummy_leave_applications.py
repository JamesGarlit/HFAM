# faculty_end/management/commands/create_dummy_leave_applications.py
from django.core.management.base import BaseCommand
from faker import Faker
from faculty_end.models import LeaveApplication
from admin_end.models import CustomUser

fake = Faker()

class Command(BaseCommand):
    help = 'Create dummy leave applications for a specific user (ID 1) for testing purposes.'

    def handle(self, *args, **options):
        # Fetch the user with ID 1
        user = CustomUser.objects.get(id=1)

        # Your dummy data creation logic here
        for _ in range(20):
            start_date = fake.date_between(start_date='-30d', end_date='today')
            start_time = fake.time()
            end_date = fake.date_between(start_date='today', end_date='+30d')
            end_time = fake.time()
            leave_type = fake.word()
            leave_reason = fake.text()
            leave_datetime_submitted = fake.date_time_this_month()
            is_viewed = fake.boolean()

            leave_application = LeaveApplication.objects.create(
                user=user,
                leave_start_date=start_date,
                leave_start_time=start_time,
                leave_end_date=end_date,
                leave_end_time=end_time,
                leave_type=leave_type,
                leave_reason=leave_reason,
                leave_datetime_submitted=leave_datetime_submitted,
                is_viewed=is_viewed,
            )

            # If you want to add supporting docs, you can do it here
            # leave_application.leave_supporting_docs = ...

        self.stdout.write(self.style.SUCCESS('Successfully created dummy leave applications for user with ID 1.'))
