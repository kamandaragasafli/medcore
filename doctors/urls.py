from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('add/', views.add_doctor, name='add'),
    path('export/', views.export_doctors_excel, name='export_excel'),
    path('<int:doctor_id>/', views.doctor_detail, name='detail'),
    path('add-payment/', views.add_doctor_payment, name='add_payment'),
    path('get-doctors-by-region/', views.get_doctors_by_region, name='get_doctors_by_region'),
]

