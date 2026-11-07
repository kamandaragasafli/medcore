from django.contrib import admin
from .models import Sale, SaleItem

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'drug', 'quantity', 'unit_price']
    list_filter = ['sale', 'drug']
    search_fields = ['sale__region__name', 'drug__ad']
    date_hierarchy = 'sale__date'
    ordering = ['-sale__date']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['region', 'date', 'total_amount', 'total_quantity']
    list_filter = ['region', 'date']
    search_fields = ['region__name']
    date_hierarchy = 'date'
    ordering = ['-date']
