from copy import deepcopy
from datetime import date

from django.test import TestCase

from restaurant.restaurant_api.models import (Address, Employee, Person,
                                              Positions, Restaurant)


class PersonModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_dict = {
            'firstname': 'Test',
            'surname': 'Test',
            'patronymic': 'Test',
            'date_of_birth': date(year=2010, month=10, day=10),
            'phone': '+199945645670',
        }
        Person.objects.create(**cls.create_dict)

    def test_get_new_person(self):
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.get(
            surname=self.create_dict['surname'],
        )
        self.assertEqual(new_person.firstname, self.create_dict['firstname'])
        self.assertEqual(new_person.patronymic, self.create_dict['patronymic'])
        self.assertEqual(
            new_person.date_of_birth,
            self.create_dict['date_of_birth'],
        )
        self.assertEqual(new_person.phone, self.create_dict['phone'])
        self.assertEqual(
            new_person.person_name,
            ' '.join(
                (self.create_dict['firstname'], self.create_dict['surname'])
            ),
        )

    def test_delete_person(self):
        new_created_dict = deepcopy(self.create_dict)
        new_created_dict['firstname'] = 'New Test'
        Person.objects.create(**new_created_dict)
        self.assertEqual(Person.objects.count(), 2)
        Person.objects.filter(
            firstname=new_created_dict['firstname'],
        ).delete()
        self.assertEqual(Person.objects.count(), 1)
        deleted_person = Person.objects.filter(
            firstname=new_created_dict['firstname'],
        )
        self.assertEqual(deleted_person.exists(), False)

    def test_update_person(self):
        firstname = 'New Test'
        Person.objects.filter(
            surname=self.create_dict['surname'],
        ).update(
            firstname=firstname
        )
        updated_person = Person.objects.get(
            surname=self.create_dict['surname'],
        )
        self.assertEqual(updated_person.firstname, firstname)


class AddressModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_dict = {
            'country': 'RU',
            'province': 'Tatarstan rep.',
            'city': 'Kazan',
            'street': 'Pushkina',
            'house': '10',
            'zip_code': '00000'
        }
        Address.objects.create(**cls.create_dict)

    def test_get_new_address(self):
        self.assertEqual(Address.objects.count(), 1)
        new_address = Address.objects.get(
            street=self.create_dict['street'],
        )
        self.assertEqual(new_address.country, self.create_dict['country'])
        self.assertEqual(new_address.house, self.create_dict['house'])
        self.assertEqual(new_address.province, self.create_dict['province'])
        self.assertEqual(new_address.city, self.create_dict['city'])
        self.assertEqual(new_address.zip_code, self.create_dict['zip_code'])
        self.assertEqual(
            new_address.full_address,
            ' '.join(
                ('Russia', self.create_dict['province'],
                 self.create_dict['city'], self.create_dict['street'],
                 self.create_dict['house'], self.create_dict['zip_code'])
            )
        )

    def test_delete_address(self):
        new_created_dict = deepcopy(self.create_dict)
        new_created_dict['street'] = 'Baumana str.'
        Address.objects.create(**new_created_dict)
        self.assertEqual(Address.objects.count(), 2)
        Address.objects.filter(
            street=new_created_dict['street'],
        ).delete()
        self.assertEqual(Address.objects.count(), 1)
        deleted_address = Address.objects.filter(
            street=new_created_dict['street'],
        )
        self.assertEqual(deleted_address.exists(), False)

    def test_update_address(self):
        house = '12D'
        Address.objects.filter(
            street=self.create_dict['street'],
        ).update(
            house=house
        )
        updated_address = Address.objects.get(
            street=self.create_dict['street'],
        )
        self.assertEqual(updated_address.house, house)


class RestaurantModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_dict = {
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }
        Restaurant.objects.create(**cls.create_dict)

    def test_get_new_restaurant(self):
        self.assertEqual(Restaurant.objects.count(), 1)
        new_restaurant = Restaurant.objects.get(
            name=self.create_dict['name'],
        )
        self.assertEqual(new_restaurant.phone, self.create_dict['phone'])
        self.assertEqual(new_restaurant.cuisine, self.create_dict['cuisine'])
        self.assertEqual(new_restaurant.rating, self.create_dict['rating'])
        self.assertEqual(str(new_restaurant), self.create_dict['name'])

    def test_delete_restaurant(self):
        new_created_dict = deepcopy(self.create_dict)
        new_created_dict['name'] = 'Sea Restaurant'
        Restaurant.objects.create(**new_created_dict)
        self.assertEqual(Restaurant.objects.count(), 2)
        Restaurant.objects.filter(
            name=new_created_dict['name'],
        ).delete()
        self.assertEqual(Restaurant.objects.count(), 1)
        deleted_restaurant = Restaurant.objects.filter(
            name=new_created_dict['name'],
        )
        self.assertEqual(deleted_restaurant.exists(), False)

    def test_update_restaurant(self):
        cuisine = 'Chineese'
        Restaurant.objects.filter(
            name=self.create_dict['name'],
        ).update(
            cuisine=cuisine
        )
        updated_restaurant = Restaurant.objects.get(
            name=self.create_dict['name'],
        )
        self.assertEqual(updated_restaurant.cuisine, cuisine)


class EmployeeModelTestCase(TestCase):

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
        cls.create_dict = {
            'restaurant_id': cls.restaurant.id,
            'person_id': cls.person.id,
            'position': Positions.DIRECTOR
        }
        Employee.objects.create(**cls.create_dict)

    def test_get_new_employee(self):
        self.assertEqual(Employee.objects.count(), 1)
        new_employee = Employee.objects.get(
            person_id=self.create_dict['person_id'],
        )
        self.assertEqual(new_employee.restaurant_id,
                         self.create_dict['restaurant_id'])
        self.assertEqual(new_employee.position, self.create_dict['position'])
        self.assertEqual(new_employee.position_name,
                         Positions.DIRECTOR.label)
        person = Person.objects.get(
            id=self.create_dict['person_id'],
        )
        restaurant = Restaurant.objects.get(
            id=self.create_dict['restaurant_id'],
        )
        self.assertEqual(
            str(new_employee),
            'Person {} in restaurant {} in position {} '.format(
                str(person), str(restaurant),
                Positions.DIRECTOR.label
            )
        )

    def test_delete_employee(self):
        person = Person.objects.create(**{
            'firstname': 'Test2',
            'surname': 'Test2',
            'patronymic': 'Test2',
            'date_of_birth': date(year=2010, month=10, day=10),
        })
        new_created_dict = deepcopy(self.create_dict)
        new_created_dict['person_id'] = person.id
        Employee.objects.create(**new_created_dict)
        self.assertEqual(Employee.objects.count(), 2)
        Employee.objects.filter(
            person_id=new_created_dict['person_id'],
        ).delete()
        self.assertEqual(Employee.objects.count(), 1)
        deleted_employee = Employee.objects.filter(
            person_id=new_created_dict['person_id'],
        )
        self.assertEqual(deleted_employee.exists(), False)

    def test_update_employee(self):
        position = Positions.MANAGER
        Employee.objects.filter(
            person_id=self.create_dict['person_id'],
        ).update(
            position=position
        )
        updated_employee = Employee.objects.get(
            person_id=self.create_dict['person_id'],
        )
        self.assertEqual(updated_employee.position, position)
