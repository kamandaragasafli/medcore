from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Doctor, DoctorPayment

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """
    Doctor Admin - Shows only doctors from the current company's database
    Works with multi-tenant architecture via middleware
    """
    
    list_display = [
        'code',
        'ad',
        'ixtisas',
        'category',
        'degree',
        'region',
        'city',
        'telefon',
        'yekun_borc',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'degree',
        'gender',
        'is_active',
        'region',
        'city',
        'ixtisas',
        'created_at'
    ]
    
    search_fields = [
        'code',
        'ad',
        'telefon',
        'email',
        'clinic__name'
    ]
    
    autocomplete_fields = ['region', 'city', 'clinic', 'ixtisas']
    
    readonly_fields = ['code', 'yekun_borc', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Əsas Məlumat', {
            'fields': ('code', 'ad', 'telefon', 'email', 'gender', 'is_active')
        }),
        ('Yer və Təşkilat', {
            'fields': ('region', 'city', 'clinic')
        }),
        ('Peşəkar Məlumat', {
            'fields': ('ixtisas', 'category', 'degree')
        }),
        ('Maliyyə Məlumatları', {
            'fields': (
                'evvelki_borc',
                'hesablanmish_miqdar',
                'silinen_miqdar',
                'yekun_borc'
            )
        }),
        ('Tarixlər', {
            'fields': ('datasiya', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        """
        Get doctors from the current tenant's database
        The middleware sets the correct database context
        """
        qs = super().get_queryset(request)
        qs = qs.select_related('region', 'city', 'clinic', 'ixtisas')
        return qs
    
    def has_module_permission(self, request):
        """
        Only show in admin if user is staff/superuser and has a company
        """
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request, 'company') and request.company is not None
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing if user has access to the company"""
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request, 'company') and request.company is not None
    
    def has_add_permission(self, request):
        """Allow adding if user has access to the company"""
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request, 'company') and request.company is not None
    
    def has_change_permission(self, request, obj=None):
        """Allow changing if user has access to the company"""
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request, 'company') and request.company is not None
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting if user has access to the company"""
        if not (request.user.is_staff or request.user.is_superuser):
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request, 'company') and request.company is not None
    
    actions = ['activate_doctors', 'deactivate_doctors', 'calculate_debts']
    
    def activate_doctors(self, request, queryset):
        """Activate selected doctors"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} həkim aktivləşdirildi.', level='SUCCESS')
    activate_doctors.short_description = "Seçilmiş həkimləri aktivləşdir"
    
    def deactivate_doctors(self, request, queryset):
        """Deactivate selected doctors"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} həkim deaktivləşdirildi.', level='WARNING')
    deactivate_doctors.short_description = "Seçilmiş həkimləri deaktivləşdir"
    
    def calculate_debts(self, request, queryset):
        """Recalculate debts for selected doctors"""
        count = 0
        for doctor in queryset:
            doctor.calculate_final_debt()
            doctor.save()
            count += 1
        self.message_user(request, f'{count} həkimin borcları yenidən hesablandı.', level='SUCCESS')
    calculate_debts.short_description = "Borcları yenidən hesabla"
    
    def save_model(self, request, obj, form, change):
        """Save with automatic debt calculation"""
        if not change:  # New object
            # Code will be auto-generated by the model
            pass
        super().save_model(request, obj, form, change)
        if change:
            self.message_user(request, f'Həkim "{obj.ad}" yeniləndi.', level='SUCCESS')
        else:
            self.message_user(request, f'Həkim "{obj.ad}" əlavə edildi. Kod: {obj.code}', level='SUCCESS')


@admin.register(DoctorPayment)
class DoctorPaymentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'region', 'payment_type', 'amount', 'date', 'created_at')
    list_filter = ('payment_type', 'region', 'date', 'created_at')
    search_fields = ('doctor__ad', 'doctor__code', 'region__name')
    autocomplete_fields = ('doctor', 'region')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
