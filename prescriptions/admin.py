from django.contrib import admin
from .models import Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1
    fields = ['drug', 'quantity', 'unit_price', 'dosage', 'duration']
    readonly_fields = []


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'region', 'doctor', 'date', 'patient_name', 'drug_count', 'total_amount', 'is_active', 'created_at']
    list_filter = ['region', 'is_active', 'date', 'created_at']
    search_fields = ['region__name', 'doctor__ad', 'patient_name', 'notes']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PrescriptionItemInline]
    
    fieldsets = (
        ('Əsas Məlumat', {
            'fields': ('region', 'doctor', 'date', 'patient_name')
        }),
        ('Qeydlər', {
            'fields': ('notes',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Tarixlər', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'drug', 'quantity', 'unit_price', 'total_price', 'dosage']
    list_filter = ['prescription__date']
    search_fields = ['drug__ad', 'prescription__doctor__ad']

