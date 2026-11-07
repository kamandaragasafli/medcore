from django.contrib import admin
from .models import Company, SubscriptionPlan, Subscription, UserProfile, ContractAgreement, Notification, NotificationTemplate


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_active', 'users_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'email', 'phone', 'address')
        }),
        ('Company Details', {
            'fields': ('license_number', 'tax_number', 'website')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_doctors', 'max_patients')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_monthly', 'price_yearly', 'is_active', 'is_popular']
    list_filter = ['plan_type', 'is_active', 'is_popular']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_doctors', 'max_patients', 'max_storage_gb')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_popular')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company', 'plan', 'status', 'billing_cycle', 'start_date', 'end_date', 'days_remaining']
    list_filter = ['status', 'billing_cycle', 'plan']
    search_fields = ['company__name']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining']
    
    fieldsets = (
        ('Subscription Info', {
            'fields': ('company', 'plan', 'status', 'billing_cycle')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'trial_end_date')
        }),
        ('Payment', {
            'fields': ('amount', 'currency', 'payment_method')
        }),
        ('Settings', {
            'fields': ('auto_renew',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'company']
    search_fields = ['user__username', 'user__email', 'company__name']
    
    fieldsets = (
        ('User & Company', {
            'fields': ('user', 'company', 'role')
        }),
        ('Profile Info', {
            'fields': ('phone', 'avatar', 'bio')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_at')
        }),
    )


@admin.register(ContractAgreement)
class ContractAgreementAdmin(admin.ModelAdmin):
    list_display = ['company', 'user', 'agreed', 'agreed_at', 'contract_version', 'created_at']
    list_filter = ['agreed', 'contract_version', 'created_at']
    search_fields = ['company__name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'agreed_at', 'ip_address']
    
    fieldsets = (
        ('Agreement Info', {
            'fields': ('company', 'user', 'contract_version')
        }),
        ('Contract Details', {
            'fields': ('contract_text',)
        }),
        ('Agreement Status', {
            'fields': ('agreed', 'agreed_at', 'ip_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['company', 'title', 'notification_type', 'is_read', 'is_important', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_important', 'created_at']
    search_fields = ['company__name', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('company', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read', 'is_important', 'read_at')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'notification_type', 'is_important', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_important', 'is_active', 'created_at']
    search_fields = ['name', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_important', 'is_active')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

