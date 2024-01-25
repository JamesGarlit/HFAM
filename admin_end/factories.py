# your_app/factories.py
import factory
from faker import Faker
from admin_end.models import CustomUser

fake = Faker()

class CustomUserFactory(factory.Factory):
    class Meta:
        model = CustomUser

    user_picture = 'user_pictures/placeholder.jpg'
    user_firstname = factory.LazyFunction(fake.first_name)
    user_middlename = factory.LazyFunction(fake.first_name)
    user_lastname = factory.LazyFunction(fake.last_name)
    extension_name = factory.LazyFunction(fake.suffix)
    employment_status = factory.LazyFunction(lambda: fake.random_element(elements=('Part-Time', 'Full-Time')))
    user_role = factory.LazyFunction(lambda: fake.random_element(elements=('Admin', 'User', 'SuperAdmin')))
    email = factory.LazyFunction(fake.email)
    is_active = factory.LazyFunction(fake.boolean)
    is_staff = factory.LazyFunction(fake.boolean)
