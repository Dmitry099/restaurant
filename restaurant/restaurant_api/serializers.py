from rest_framework import serializers

from .constants import RATING_MAX_VALUE
from .models import Address, Employee, Person, Restaurant


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'


class RestaurantSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=0, max_value=RATING_MAX_VALUE)

    class Meta:
        model = Restaurant
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeFullInfoSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='person.person_name')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Employee
        fields = ('id', 'employee_name', 'restaurant_name', 'position_name')


class EmployeeRelatedSerializer(serializers.RelatedField):
    employee_name = serializers.ReadOnlyField(source='person.person_name')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    def to_representation(self, value):
        return value.person_name

    class Meta:
        model = Employee


class RestaurantFullInfoSerializer(serializers.ModelSerializer):
    full_address = serializers.ReadOnlyField(source='address.full_address')
    employees = EmployeeRelatedSerializer(read_only=True, many=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'phone', 'cuisine', 'rating',
                  'full_address', 'employees')
