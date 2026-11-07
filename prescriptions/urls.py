from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    path('', views.prescription_list, name='list'),
    path('add/', views.add_prescription, name='add'),
    path('api/doctors/<int:region_id>/', views.doctors_by_region, name='doctors_by_region'),
    path('api/last-closed-report/<int:region_id>/', views.get_last_closed_report, name='last_closed_report'),
    path('lists/', views.prescription_list, name='lists'),
    path('filter-ajax/', views.filter_prescriptions_ajax, name='filter_ajax'),

    path('monthly/', views.prescription_monthly_report, name='monthly'),
    path('export/', views.export_prescriptions_excel, name='export_excel'),

]

