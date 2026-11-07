from django.urls import path
from . import views

app_name = 'drugs'

urlpatterns = [
    path('', views.drug_list, name='list'),
    path('add/', views.add_drug, name='add'),
    path('<int:drug_id>/', views.drug_detail, name='detail'),
]

