"""
Master Admin Panel URLs
"""

from django.urls import path
from . import views

app_name = 'master_admin'

urlpatterns = [
    path('', views.master_dashboard, name='dashboard'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    path('companies/<int:company_id>/switch/', views.switch_to_company, name='switch_to_company'),
    path('companies/<int:company_id>/export-doctors/', views.export_company_doctors_excel, name='export_company_doctors'),
    path('companies/<int:company_id>/export-debts/', views.export_company_debts_excel, name='export_company_debts'),
    path('companies/<int:company_id>/zero-debts/', views.zero_company_doctors_debts, name='zero_company_debts'),
    path('companies/<int:company_id>/import-debts/', views.import_company_debts_excel, name='import_company_debts'),
    path('companies/<int:company_id>/import-doctors-full/', views.import_company_doctors_full_excel, name='import_company_doctors_full'),
    path('companies/<int:company_id>/import-drugs/', views.import_company_drugs_excel, name='import_company_drugs'),
    path('exit-impersonation/', views.exit_impersonation, name='exit_impersonation'),
    path('analytics/', views.platform_analytics, name='analytics'),
    path('users/', views.user_management, name='user_management'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notifications/send/<int:company_id>/', views.send_notification, name='send_notification'),
]

