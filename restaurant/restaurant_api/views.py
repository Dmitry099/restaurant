from abc import abstractmethod

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Address, Employee, Person, Restaurant
from .serializers import (AddressSerializer, EmployeeFullInfoSerializer,
                          EmployeeSerializer, PersonSerializer,
                          RestaurantFullInfoSerializer, RestaurantSerializer)


class SeparateListViewSet(viewsets.ModelViewSet):
    """
    API endpoint for entities that should have separate list serializer.
    """

    @property
    @abstractmethod
    def serializer_list_class(self):
        None

    def get_serializer_class(self, *args, **kwargs):
        """Get class of serializer by action."""
        if self.action == 'list':
            return self.serializer_list_class
        else:
            return self.serializer_class


class PersonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows persons to be viewed or edited.
    """
    queryset = Person.objects.all().order_by('surname', 'firstname')
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]


class AddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows addresses to be viewed or edited.
    """
    queryset = Address.objects.all().order_by('country')
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]


class RestaurantViewSet(SeparateListViewSet):
    """
    API endpoint that allows restaurants to be viewed or edited.
    """
    queryset = Restaurant.objects.all().select_related(
        'address'
    ).prefetch_related(
        'employees'
    ).order_by('name')
    serializer_class = RestaurantSerializer
    serializer_list_class = RestaurantFullInfoSerializer
    lookup_field = 'name'
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False)
    def get_random_restaurant(self, request, **kwargs):
        """Get random restaurant info."""
        restaurant = Restaurant.objects.order_by(
            '?'
        ).select_related(
            'address'
        ).prefetch_related(
            'employees'
        ).first()
        serializer = RestaurantFullInfoSerializer(restaurant)
        return Response(serializer.data)


class EmployeeViewSet(SeparateListViewSet):
    """
    API endpoint that allows employees to be viewed or edited.
    """
    queryset = Employee.objects.all().order_by(
        'id'
    ).select_related(
        'person', 'restaurant'
    )
    serializer_class = EmployeeSerializer
    serializer_list_class = EmployeeFullInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
