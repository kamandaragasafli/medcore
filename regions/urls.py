from django.urls import path
from . import views

app_name = 'regions'

urlpatterns = [
    # Region URLs
    path('', views.region_list, name='list'),
    path('add/', views.add_region, name='add'),
    
    # City URLs
    path('cities/', views.city_list, name='city_list'),
    path('cities/add/', views.add_city, name='add_city'),
    
    # Clinic URLs
    path('clinics/', views.clinic_list, name='clinic_list'),
    path('clinics/add/', views.add_clinic, name='add_clinic'),
    
    # Specialization URLs
    path('specializations/', views.specialization_list, name='specialization_list'),
    path('specializations/add/', views.add_specialization, name='add_specialization'),
]

