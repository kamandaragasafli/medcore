from django.urls import path
from . import views

app_name = 'subscription'

urlpatterns = [
    # path('plans/', views.subscription_plans, name='plans'),  # Gizlədilib
    path('register/', views.register_company, name='register'),
    path('contract/', views.contract_view, name='contract'),
    path('success/', views.subscription_success, name='success'),
]

