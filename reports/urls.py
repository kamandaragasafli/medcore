from django.urls import path

from .views import monthly_reports, export_reports_excel, close_month_report

app_name = 'reports'

urlpatterns = [
    path('', monthly_reports, name='list'),
    path('export/', export_reports_excel, name='export_excel'),
    path("close/", close_month_report, name="close"),
    
]

