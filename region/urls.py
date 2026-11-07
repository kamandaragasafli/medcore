from django.urls import path

from .views import region_list

app_name = 'region'

urlpatterns = [
    path('', region_list, name='list'),
]

