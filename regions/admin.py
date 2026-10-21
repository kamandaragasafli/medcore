from django.contrib import admin
from .models import Region, City, Clinic, Specialization


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def has_module_permission(self, request):
        """Allow access if user is staff or superuser"""
        return request.user.is_staff or request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region']
    search_fields = ['name']
    list_filter = ['region']
    ordering = ['name']
    autocomplete_fields = ['region']
    
    def has_module_permission(self, request):
        """Allow access if user is staff or superuser"""
        return request.user.is_staff or request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'city', 'type', 'is_active']
    search_fields = ['name', 'address']
    list_filter = ['type', 'is_active', 'region', 'city']
    ordering = ['name']
    autocomplete_fields = ['region', 'city']
    fieldsets = (
        ('Əsas Məlumat', {
            'fields': ('name', 'type', 'is_active')
        }),
        ('Yer Məlumatı', {
            'fields': ('region', 'city', 'address')
        }),
        ('Əlaqə Məlumatları', {
            'fields': ('phone',)
        }),
    )
    
    def has_module_permission(self, request):
        """Allow access if user is staff or superuser"""
        return request.user.is_staff or request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']
    ordering = ['code', 'name']
    
    def has_module_permission(self, request):
        """Allow access if user is staff or superuser"""
        return request.user.is_staff or request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser
