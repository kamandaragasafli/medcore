from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Company(models.Model):
    """
    Company/Organization for this deployment.
    One company per install (copy the app for another customer).
    """
    name = models.CharField(max_length=200, verbose_name='Company Name')
    slug = models.SlugField(unique=True, max_length=200)
    email = models.EmailField(unique=True, verbose_name='Company Email')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Branding
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name='Company Logo')

    # Company Details
    license_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Medical License')
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='VÖEN')
    website = models.URLField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Subscription Info
    max_users = models.IntegerField(default=5, help_text='Maximum number of users allowed')
    max_doctors = models.IntegerField(default=10, help_text='Maximum number of doctors')
    max_patients = models.IntegerField(default=100, help_text='Maximum number of patients')
    
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def users_count(self):
        return self.userprofile_set.count()
    
    @property
    def active_subscription(self):
        """Get the active subscription"""
        return self.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()


class SubscriptionPlan(models.Model):
    """
    Subscription Plans (Basic, Professional, Enterprise)
    """
    PLAN_TYPES = [
        ('starter', 'Starter'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField()
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Limits
    max_users = models.IntegerField(default=5)
    max_doctors = models.IntegerField(default=10)
    max_patients = models.IntegerField(default=100)
    max_storage_gb = models.IntegerField(default=5, help_text='Storage in GB')
    
    # Features
    features = models.JSONField(default=list, help_text='List of features')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price_monthly']
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/month"


class Subscription(models.Model):
    """
    Company Subscription Model
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ]
    
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    # Subscription Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CHOICES, default='monthly')
    
    # Dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(blank=True, null=True)
    
    # Payment
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.plan.name} ({self.status})"
    
    @property
    def is_valid(self):
        return self.status == 'active' and self.end_date >= timezone.now()
    
    @property
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now()
            return delta.days
        return 0
    
    def save(self, *args, **kwargs):
        # Set end_date based on billing cycle
        if not self.end_date:
            if self.billing_cycle == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            else:  # yearly
                self.end_date = self.start_date + timedelta(days=365)
        
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended User Profile with Company Link
    """
    ROLE_CHOICES = [
        ('owner', 'Company Owner'),
        ('admin', 'Administrator'),
        ('doctor', 'Doctor'),
        ('staff', 'Staff'),
        ('user', 'User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_profiles')
    
    # Role & Permissions
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Profile Info
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'company']
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name}"


class ContractAgreement(models.Model):
    """
    Contract Agreement Model - Tracks user acceptance of terms
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contract_agreements')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_agreements')
    
    # Contract details
    contract_version = models.CharField(max_length=50, default='1.0')
    contract_text = models.TextField(help_text='Full contract text at time of acceptance')
    
    # Agreement
    agreed = models.BooleanField(default=False)
    agreed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contract Agreement'
        verbose_name_plural = 'Contract Agreements'
        ordering = ['-created_at']
        unique_together = ['company', 'user']
    
    def __str__(self):
        return f"{self.company.name} - {self.user.username} - {'Agreed' if self.agreed else 'Pending'}"


class Notification(models.Model):
    """
    Notification Model - System notifications for companies
    """
    NOTIFICATION_TYPES = [
        ('info', 'Məlumat'),
        ('warning', 'Xəbərdarlıq'),
        ('success', 'Uğur'),
        ('error', 'Xəta'),
        ('subscription', 'Abunəlik'),
    ]
    
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name='Şirkət'
    )
    
    # Notification details
    title = models.CharField(max_length=200, verbose_name='Başlıq')
    message = models.TextField(verbose_name='Mesaj')
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='info',
        verbose_name='Növ'
    )
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name='Oxunub')
    is_important = models.BooleanField(default=False, verbose_name='Vacib')
    
    # Metadata
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sent_notifications',
        verbose_name='Göndərən'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma tarixi')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Oxunma tarixi')
    
    # Optional link
    action_url = models.URLField(blank=True, null=True, verbose_name='Əlaqəli link')
    action_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Link mətni')
    
    class Meta:
        verbose_name = 'Bildiriş'
        verbose_name_plural = 'Bildirişlər'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'is_read']),
            models.Index(fields=['company', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class NotificationTemplate(models.Model):
    """
    Pre-made notification templates for quick sending
    """
    NOTIFICATION_TYPES = [
        ('info', 'Məlumat'),
        ('warning', 'Xəbərdarlıq'),
        ('success', 'Uğur'),
        ('error', 'Xəta'),
        ('subscription', 'Abunəlik'),
    ]
    
    name = models.CharField(
        max_length=200, 
        verbose_name='Şablon adı',
        help_text='Məsələn: Sistem işləməsi haqqında'
    )
    title = models.CharField(max_length=200, verbose_name='Başlıq')
    message = models.TextField(verbose_name='Mesaj')
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='info',
        verbose_name='Növ'
    )
    is_important = models.BooleanField(default=False, verbose_name='Vacib')
    action_url = models.URLField(blank=True, null=True, verbose_name='Əlaqəli link')
    action_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Link mətni')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bildiriş Şablonu'
        verbose_name_plural = 'Bildiriş Şablonları'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BackupSettings(models.Model):
    """
    Backup Settings Model - Company backup configuration
    """
    INTERVAL_CHOICES = [
        ('disabled', 'Deaktiv'),
        ('daily', 'Günlük'),
        ('weekly', 'Həftəlik'),
        ('monthly', 'Aylıq'),
    ]
    
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='backup_settings',
        verbose_name='Şirkət'
    )
    
    interval = models.CharField(
        max_length=20,
        choices=INTERVAL_CHOICES,
        default='disabled',
        verbose_name='Backup Aralığı'
    )
    
    retention_days = models.IntegerField(
        default=30,
        verbose_name='Saxlama Müddəti (gün)',
        help_text='Köhnə backup-lar neçə gün saxlanacaq'
    )
    
    last_backup = models.DateTimeField(null=True, blank=True, verbose_name='Son Backup')
    next_backup = models.DateTimeField(null=True, blank=True, verbose_name='Növbəti Backup')
    
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Backup Parametrləri'
        verbose_name_plural = 'Backup Parametrləri'
    
    def __str__(self):
        return f"{self.company.name} - {self.get_interval_display()}"


class Backup(models.Model):
    """
    Backup Model - Stores backup file information
    """
    STATUS_CHOICES = [
        ('pending', 'Gözləyir'),
        ('success', 'Uğurlu'),
        ('failed', 'Uğursuz'),
    ]
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='backups',
        verbose_name='Şirkət'
    )
    
    file_path = models.CharField(max_length=500, verbose_name='Fayl Yolu')
    file_name = models.CharField(max_length=200, verbose_name='Fayl Adı')
    file_size = models.BigIntegerField(default=0, verbose_name='Fayl Ölçüsü (bytes)')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    error_message = models.TextField(blank=True, null=True, verbose_name='Xəta Mesajı')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılma Tarixi')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_backups',
        verbose_name='Yaradan'
    )
    
    class Meta:
        verbose_name = 'Backup'
        verbose_name_plural = 'Backup-lar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.file_name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"