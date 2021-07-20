from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from restaurant.restaurant_api import views

router = routers.DefaultRouter()
router.register(r'persons', views.PersonViewSet)
router.register(r'address', views.AddressViewSet)
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'employees', views.EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
    path('admin/', admin.site.urls),
]
