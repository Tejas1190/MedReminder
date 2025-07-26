from django.urls import path
from .views import geofencing_page, geofencing_add, geofencing_delete, toggle_geofencing

urlpatterns = [
    path('', geofencing_page, name='geofencing_page'),
    path('add/', geofencing_add, name='geofencing_add'),
    path('delete/<int:zone_id>/', geofencing_delete, name='geofencing_delete'),
    path('toggle/', toggle_geofencing, name='toggle_geofencing'),
] 