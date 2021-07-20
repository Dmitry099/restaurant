import json
from copy import deepcopy
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from restaurant.restaurant_api.models import (Address, Employee, Person,
                                              Positions, Restaurant)
from restaurant.restaurant_api.serializers import (
    AddressSerializer, EmployeeFullInfoSerializer, EmployeeSerializer,
    PersonSerializer, RestaurantFullInfoSerializer, RestaurantSerializer)


class CheckLoginUserTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.login_url = reverse('rest_framework:login')
        cls.login_dict = {
            'username': 'test_User',
            'password': 'test_Pass',
        }
        User.objects.create_user(username=cls.login_dict['username'],
                                 password=cls.login_dict['password'])

    def test_log_in(self):
        response = self.client.post(self.login_url, self.login_dict)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)

    def test_log_in_with_not_exists_user(self):
        incorrect_login_dict = {
            'username': 'test_User2',
            'password': 'test_Pass2',
        }
        login = self.client.login(**incorrect_login_dict)
        self.assertFalse(login)

    def test_log_in_with_incorrect_password(self):
        login_dict = deepcopy(self.login_dict)
        login_dict['password'] = 'test'
        login = self.client.login(**login_dict)
        self.assertFalse(login)


class UserTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'TestCase'
        cls.password = 'Password'

        User.objects.create_user(
            username=cls.username,
            password=cls.password
        )

    def setUp(self):
        login = self.client.login(
            username=self.username, password=self.password)
        if not login:
            raise HttpResponseForbidden()


class PersonCreateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.person_url = reverse('person-list')
        cls.create_dict = {
            'firstname': 'Test',
            'surname': 'Test',
            'patronymic': 'Test',
            'date_of_birth': date(year=2010, month=10, day=10),
            'phone': '+199945645670',
        }

    def test_create_person(self):
        response = self.client.post(self.person_url, self.create_dict)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Person.objects.count(), 1)
        new_person = Person.objects.get(
            firstname=self.create_dict['firstname'],
            surname=self.create_dict['surname'],
        )
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

    def test_create_person_without_required_fields(self):
        create_dict = deepcopy(self.create_dict)
        del create_dict['firstname']
        response = self.client.post(self.person_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['firstname'][0]),
            'This field is required.',
        )

    def test_create_person_with_incorrect_field(self):
        create_dict = deepcopy(self.create_dict)
        create_dict['date_of_birth'] = 1
        response = self.client.post(self.person_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['date_of_birth'][0]),
            'Date has wrong format. Use one of these formats instead: '
            'YYYY-MM-DD.',
        )


class PersonGetAllViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.person_url = reverse('person-list')
        Person.objects.bulk_create([
            Person(
                firstname='Test',
                surname='Test',
                patronymic='Test',
                date_of_birth=date(year=2010, month=10, day=10),
                phone='+199945645670',
            ),
            Person(
                firstname='Test2',
                surname='Test2',
            ),
            Person(
                firstname='Test3',
                surname='Test3',
            )
        ])

    def test_get_all_persons(self):
        response = self.client.get(self.person_url)
        persons = Person.objects.all()
        serializer = PersonSerializer(persons, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class PersonGetViewTestCase(UserTestCase):

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
        cls.person = Person.objects.create(**cls.create_dict)

    def test_get_valid_single_person(self):
        response = self.client.get(
            reverse('person-detail', kwargs={'pk': self.person.pk})
        )
        person = Person.objects.get(pk=self.person.pk)
        serializer = PersonSerializer(person)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_single_person(self):
        response = self.client.get(
            reverse('person-detail', kwargs={'pk': 30})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PersonDeleteViewTestCase(UserTestCase):

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
        cls.person = Person.objects.create(**cls.create_dict)

    def test_valid_delete_person(self):
        response = self.client.delete(
            reverse('person-detail', kwargs={'pk': self.person.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_person(self):
        response = self.client.delete(
            reverse('person-detail', kwargs={'pk': 30})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PersonUpdateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.person = Person.objects.create(**{
            'firstname': 'Test',
            'surname': 'Test',
            'patronymic': 'Test',
            'date_of_birth': date(year=2010, month=10, day=10),
            'phone': '+199945645670',
        })
        cls.valid_payload = {
            'firstname': 'Test',
            'surname': 'Test2',
            'patronymic': 'Test2',
            'date_of_birth': '2010-10-10',
            'phone': '+199945645670',
        }
        cls.invalid_payload = {
            'firstname': '',
            'surname': '',
            'patronymic': 'Test',
            'date_of_birth': '2010-10-10',
            'phone': '+199945645670',
        }

    def test_valid_update_person(self):
        response = self.client.put(
            reverse('person-detail', kwargs={'pk': self.person.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_person(self):
        response = self.client.put(
            reverse('person-detail', kwargs={'pk': self.person.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['firstname'][0]),
            'This field may not be blank.',
        )
        self.assertEqual(
            str(response.data['surname'][0]),
            'This field may not be blank.',
        )


class AddressCreateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address_url = reverse('address-list')
        cls.create_dict = {
            'country': 'RU',
            'province': 'Tatarstan rep.',
            'city': 'Kazan',
            'street': 'Pushkina',
            'house': '10',
            'zip_code': '00000'
        }

    def test_create_address(self):
        response = self.client.post(self.address_url, self.create_dict)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 1)
        new_address = Address.objects.get(
            street=self.create_dict['street'],
        )
        self.assertEqual(new_address.house, self.create_dict['house'])
        self.assertEqual(new_address.country, self.create_dict['country'])
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

    def test_create_address_without_required_fields(self):
        create_dict = deepcopy(self.create_dict)
        del create_dict['country']
        response = self.client.post(self.address_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['country'][0]),
            'This field is required.',
        )

    def test_create_address_with_incorrect_field(self):
        create_dict = deepcopy(self.create_dict)
        create_dict['zip_code'] = '111111111'
        response = self.client.post(self.address_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['zip_code'][0]),
            'Ensure this field has no more than 5 characters.',
        )


class AddressGetAllViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address_url = reverse('address-list')
        Address.objects.bulk_create([
            Address(
                country='RU',
                province='Tatarstan rep.',
                city='Kazan',
                street='Pushkina',
                house='10',
                zip_code='00000'
            ),
            Address(
                country='RU',
                province='Tatarstan rep.',
                city='Kazan',
                street='Baumana str.',
                house='11',
            ),
            Address(
                country='RU',
                province='Tatarstan rep.',
                city='Kazan',
                street='Pushkina',
                house='12',
            )
        ])

    def test_get_all_addresses(self):
        response = self.client.get(self.address_url)
        addresses = Address.objects.all()
        serializer = AddressSerializer(addresses, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class AddressGetViewTestCase(UserTestCase):

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
        cls.address = Address.objects.create(**cls.create_dict)

    def test_get_valid_single_address(self):
        response = self.client.get(
            reverse('address-detail', kwargs={'pk': self.address.pk})
        )
        address = Address.objects.get(pk=self.address.pk)
        serializer = AddressSerializer(address)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_single_address(self):
        response = self.client.get(
            reverse('address-detail', kwargs={'pk': 30})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddressDeleteViewTestCase(UserTestCase):

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
        cls.address = Address.objects.create(**cls.create_dict)

    def test_valid_delete_address(self):
        response = self.client.delete(
            reverse('address-detail', kwargs={'pk': self.address.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_address(self):
        response = self.client.delete(
            reverse('address-detail', kwargs={'pk': 30})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddressUpdateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address = Address.objects.create(**{
            'country': 'RU',
            'province': 'Tatarstan rep.',
            'city': 'Kazan',
            'street': 'Pushkina',
            'house': '10',
            'zip_code': '00000'
        })
        cls.valid_payload = {
            'country': 'RU',
            'province': 'Moscow region',
            'city': 'Tula',
            'street': 'Lenina',
            'house': '1',
        }
        cls.invalid_payload = {
            'province': 'Moscow region',
            'city': 'Tula',
            'street': 'Lenina',
            'house': '1',
        }

    def test_valid_update_address(self):
        response = self.client.put(
            reverse('address-detail', kwargs={'pk': self.address.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_address(self):
        response = self.client.put(
            reverse('address-detail', kwargs={'pk': self.address.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['country'][0]),
            'This field is required.',
        )


class RestaurantCreateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restaurant_url = reverse('restaurant-list')
        cls.create_dict = {
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }

    def test_create_restaurant(self):
        response = self.client.post(self.restaurant_url,
                                    self.create_dict)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 1)
        new_restaurant = Restaurant.objects.get(
            name=self.create_dict['name'],
        )
        self.assertEqual(new_restaurant.phone, self.create_dict['phone'])
        self.assertEqual(new_restaurant.cuisine, self.create_dict['cuisine'])
        self.assertEqual(new_restaurant.rating, self.create_dict['rating'])

    def test_create_restaurant_without_required_fields(self):
        create_dict = deepcopy(self.create_dict)
        del create_dict['name']
        response = self.client.post(self.restaurant_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['name'][0]),
            'This field is required.',
        )

    def test_create_restaurant_with_incorrect_field(self):
        create_dict = deepcopy(self.create_dict)
        create_dict['rating'] = 150
        response = self.client.post(self.restaurant_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['rating'][0]),
            'Ensure this value is less than or equal to 100.',
        )


class RestaurantGetAllViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restaurant_url = reverse('restaurant-list')
        Restaurant.objects.bulk_create([
            Restaurant(
                name='Russian wolf',
                phone='+199945645670',
                cuisine='Russian',
                rating=100,
            ),
            Restaurant(
                name='Russian wolf2',
                phone='+199945645671',
                cuisine='Russian',
                rating=99,
            ),
            Restaurant(
                name='Russian wolf3',
                phone='+199945645672',
                cuisine='Russian',
                rating=98,
            )
        ])

    def test_get_all_restaurants(self):
        response = self.client.get(self.restaurant_url)
        restaurants = Restaurant.objects.all()
        serializer = RestaurantFullInfoSerializer(restaurants, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class RestaurantGetViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_dict = {
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }
        cls.restaurant = Restaurant.objects.create(**cls.create_dict)

    def test_get_valid_single_restaurant(self):
        response = self.client.get(
            reverse('restaurant-detail', kwargs={'name': self.restaurant.name})
        )
        restaurant = Restaurant.objects.get(pk=self.restaurant.pk)
        serializer = RestaurantSerializer(restaurant)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_single_restaurant(self):
        response = self.client.get(
            reverse('restaurant-detail', kwargs={'name': 'New name'})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_random_single_restaurant(self):
        response = self.client.get(reverse('restaurant-get-random-restaurant'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        restaurant = Restaurant.objects.get(pk=response.data['id'])
        serializer = RestaurantFullInfoSerializer(restaurant)
        self.assertEqual(response.data, serializer.data)


class RestaurantDeleteViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_dict = {
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }
        cls.restaurant = Restaurant.objects.create(**cls.create_dict)

    def test_valid_delete_restaurant(self):
        response = self.client.delete(
            reverse('restaurant-detail', kwargs={'name': self.restaurant.name})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_restaurant(self):
        response = self.client.delete(
            reverse('restaurant-detail', kwargs={'name': 'New Name'})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RestaurantUpdateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.restaurant = Restaurant.objects.create(**{
            'name': 'Russian wolf',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        })
        cls.valid_payload = {
            'name': 'Russian wolf2',
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }
        cls.invalid_payload = {
            'phone': '+199945645670',
            'cuisine': 'Russian',
            'rating': 100,
        }

    def test_valid_update_restaurant(self):
        response = self.client.put(
            reverse('restaurant-detail',
                    kwargs={'name': self.restaurant.name}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_restaurant(self):
        response = self.client.put(
            reverse('restaurant-detail',
                    kwargs={'name': self.restaurant.name}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['name'][0]),
            'This field is required.',
        )


class EmployeeCreateViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_url = reverse('employee-list')
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
            'restaurant': cls.restaurant.id,
            'person': cls.person.id,
            'position': Positions.DIRECTOR
        }

    def test_create_employee(self):
        response = self.client.post(self.employee_url, self.create_dict)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        new_restaurant = Employee.objects.get(
            position=Positions.DIRECTOR,
        )
        self.assertEqual(new_restaurant.restaurant_id,
                         self.create_dict['restaurant'])
        self.assertEqual(new_restaurant.person_id, self.create_dict['person'])

    def test_create_employee_without_required_fields(self):
        create_dict = deepcopy(self.create_dict)
        del create_dict['position']
        response = self.client.post(self.employee_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['position'][0]),
            'This field is required.',
        )

    def test_create_employee_with_incorrect_field(self):
        create_dict = deepcopy(self.create_dict)
        create_dict['position'] = 100
        response = self.client.post(self.employee_url, create_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['position'][0]),
            '"100" is not a valid choice.',
        )


class EmployeeGetAllViewTestCase(UserTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee_url = reverse('employee-list')
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
        cls.restaurant_2 = Restaurant.objects.create(**{
            'name': 'Russian wolf2',
            'phone': '+199945645671',
            'cuisine': 'Russian',
            'rating': 100,
        })
        cls.person_2 = Person.objects.create(**{
            'firstname': 'Test2',
            'surname': 'Test2',
            'patronymic': 'Test2',
            'date_of_birth': date(year=2012, month=10, day=10),
            'phone': '+199945645671',
        })
        cls.create_dict = {

        }
        Employee.objects.bulk_create([
            Employee(
                restaurant=cls.restaurant,
                person=cls.person,
                position=Positions.DIRECTOR
            ),
            Employee(
                restaurant=cls.restaurant_2,
                person=cls.person_2,
                position=Positions.MANAGER
            ),
            Employee(
                restaurant=cls.restaurant_2,
                person=cls.person,
                position=Positions.MANAGER
            ),
        ])

    def test_get_all_employees(self):
        response = self.client.get(self.employee_url)
        employees = Employee.objects.all()
        serializer = EmployeeFullInfoSerializer(employees, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class EmployeeGetViewTestCase(UserTestCase):

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
        cls.employee = Employee.objects.create(**cls.create_dict)

    def test_get_valid_single_employee(self):
        response = self.client.get(
            reverse('employee-detail', kwargs={'pk': self.employee.pk})
        )
        employee = Employee.objects.get(pk=self.restaurant.pk)
        serializer = EmployeeSerializer(employee)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_single_employee(self):
        response = self.client.get(
            reverse('employee-detail', kwargs={'pk': 30})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EmployeeDeleteViewTestCase(UserTestCase):

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
        cls.employee = Employee.objects.create(**cls.create_dict)

    def test_valid_delete_employee(self):
        response = self.client.delete(
            reverse('employee-detail', kwargs={'pk': self.employee.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_employee(self):
        response = self.client.delete(
            reverse('employee-detail', kwargs={'pk': 30})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EmployeeUpdateViewTestCase(UserTestCase):

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
        cls.employee = Employee.objects.create(**{
            'restaurant_id': cls.restaurant.id,
            'person_id': cls.person.id,
            'position': Positions.DIRECTOR
        })
        cls.valid_payload = {
            'restaurant': cls.restaurant.id,
            'person': cls.person.id,
            'position': Positions.MANAGER
        }
        cls.invalid_payload = {
            'person': cls.person.id,
            'position': Positions.MANAGER
        }

    def test_valid_update_employee(self):
        response = self.client.put(
            reverse('employee-detail', kwargs={'pk': self.employee.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_employee(self):
        response = self.client.put(
            reverse('employee-detail', kwargs={'pk': self.employee.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data['restaurant'][0]),
            'This field is required.',
        )
