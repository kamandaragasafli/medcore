from django.urls import path

from .views import monthly_sales, add_sale, sale_list, edit_sale

app_name = 'sales'

urlpatterns = [
    path('', monthly_sales, name='list'),
    path('add/', add_sale, name='add'),
    path('records/', sale_list, name='sale_list'),
    path('<int:sale_id>/edit/', edit_sale, name='edit'),
]

