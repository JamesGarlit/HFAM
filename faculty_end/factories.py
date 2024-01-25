# faculty_end/factories.py
import factory
from faker import Faker
from admin_end.factories import CustomUserFactory
from faculty_end.models import LeaveApplication

fake = Faker()

class LeaveApplicationFactory(factory.Factory):
    class Meta:
        model = LeaveApplication

    user = factory.SubFactory(CustomUserFactory)
    leave_start_date = fake.date_between(start_date='-30d', end_date='today')  # Random date in the last 30 days
    leave_start_time = fake.time()
    leave_end_date = fake.date_between(start_date='today', end_date='+30d')  # Random date in the next 30 days
    leave_end_time = fake.time()
    leave_type = fake.word()
    leave_reason = fake.text()
    leave_supporting_docs = None  # Modify as needed based on your requirements
    leave_datetime_submitted = fake.date_time_this_month()  # Random date time in the current month
    is_viewed = fake.boolean()
