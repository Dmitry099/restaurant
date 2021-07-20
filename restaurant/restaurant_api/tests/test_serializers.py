from datetime import date

from django.test import TestCase

from restaurant.restaurant_api.models import (Address, Employee, Person,
                                              Positions, Restaurant)
from restaurant.restaurant_api.serializers import (AddressSerializer,
                                                   EmployeeSerializer,
                                                   PersonSerializer,
                                                   RestaurantSerializer)


class PersonSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.person_dict = {
            'firstname': 'Test',
            'surname': 'Test',
            'patronymic': 'Test',
            'date_of_birth': date(year=2010, month=10, day=10),
            'phone': '+199945645670',
        }

        cls.person = Person.objects.create(**cls.person_dict)
        cls.serializer = PersonSerializer(instance=cls.person)

    def test_person_serializer_has_expected_fields(self):
        self.assertCountEqual(
            self.serializer.data,
            ['id', 'firstname', 'surname', 'patronymic', 'date_of_birth',
             'phone']
        )

    def test_person_serializer_field_content(self):

        self.assertEqual(self.serializer.data['firstname'],
                         self.person_dict['firstname'])
        self.assertEqual(self.serializer.data['surname'],
                         self.person_dict['surname'])
        self.assertEqual(self.serializer.data['patronymic'],
                         self.person_dict['patronymic'])
        self.assertEqual(self.serializer.data['date_of_birth'],
                         self.person_dict['date_of_birth'].strftime(
                             '%Y-%m-%d'
                         ))
        self.assertEqual(self.serializer.data['phone'],
                         self.person_dict['phone'])


class AddressSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address_dict = {
            'country': 'RU',
            'province': 'Tatarstan rep.',
            'city': 'Kazan',
            'street': 'Pushkina',
            'house': '10',
            'zip_code': '00000'
        }
        cls.address = Address.objects.create(**cls.address_dict)
        cls.serializer = AddressSerializer(instance=cls.address)

    def test_address_serializer_has_expected_fields(self):
        self.assertCountEqual(
            self.serializer.data,
            ['id', 'country', 'province', 'city', 'street', 'house',
             'zip_code']
        )

    def test_address_serializer_field_content(self):
        self.assertEqual(self.serializer.data['country'],
                         self.address_dict['country'])
        self.assertEqual(self.serializer.data['province'],
                         self.address_dict['province'])
        self.assertEqual(self.serializer.data['city'],
                         self.address_dict['city'])
        self.assertEqual(self.serializer.data['street'],
                         self.address_dict['street'])
        self.assertEqual(self.serializer.data['house'],
                         self.address_dict['house'])
        self.assertEqual(self.serializer.data['zip_code'],
                         self.address_dict['zip_code'])


class RestaurantSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restaurant_dict = {
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }

        cls.restaurant = Restaurant.objects.create(**cls.restaurant_dict)
        cls.serializer = RestaurantSerializer(instance=cls.restaurant)

    def test_restaurant_serializer_has_expected_fields(self):
        self.assertCountEqual(
            self.serializer.data,
            ['id', 'name', 'phone', 'cuisine', 'rating', 'address',
             'employees']
        )

    def test_restaurant_serializer_field_content(self):

        self.assertEqual(self.serializer.data['name'],
                         self.restaurant_dict['name'])
        self.assertEqual(self.serializer.data['phone'],
                         self.restaurant_dict['phone'])
        self.assertEqual(self.serializer.data['cuisine'],
                         self.restaurant_dict['cuisine'])
        self.assertEqual(self.serializer.data['rating'],
                         self.restaurant_dict['rating'])

    def test_restaurant_save_not_allowed_rating(self):
        serializer_data = {
            'name': 'Great Time',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 150,
        }
        serializer = RestaurantSerializer(data=serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set(['rating']))

    def test_restaurant_save_with_not_unique_name(self):
        serializer_data = {
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }
        serializer = RestaurantSerializer(data=serializer_data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors), set(['name']))


class EmployeeSerializerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restaurant = Restaurant.objects.create(**{
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        })
        cls.person = Person.objects.create(**{
            'firstname': 'Test',
            'surname': 'Test',
            'patronymic': 'Test',
            'date_of_birth': date(year=2010, month=10, day=10),
            'phone': '+199945645670',
        })
        cls.employee_dict = {
            'restaurant': cls.restaurant,
            'person': cls.person,
            'position': Positions.DIRECTOR
        }

        cls.employee = Employee.objects.create(**cls.employee_dict)
        cls.serializer = EmployeeSerializer(instance=cls.employee)

    def test_employee_serializer_has_expected_fields(self):
        self.assertCountEqual(
            self.serializer.data,
            ['id', 'restaurant', 'person', 'position']
        )

    def test_employee_serializer_field_content(self):
        self.assertEqual(self.serializer.data['restaurant'],
                         self.employee_dict['restaurant'].id)
        self.assertEqual(self.serializer.data['person'],
                         self.employee_dict['person'].id)
        self.assertEqual(self.serializer.data['position'],
                         self.employee_dict['position'])

    def test_employee_save_with_not_unique_person_and_restaurant(self):
        employee_dict = {
            'restaurant': self.restaurant.pk,
            'person': self.person.pk,
            'position': Positions.MANAGER
        }
        serializer = EmployeeSerializer(data=employee_dict)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors['non_field_errors'][0],
            'The fields restaurant, person must make a unique set.'
        )
