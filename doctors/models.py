from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from regions.models import Region, City, Clinic, Specialization
import random
import string


class Doctor(models.Model):
    """Həkim (Doctor) Model"""
    
    GENDER_CHOICES = [
        ('male', 'Kişi'),
        ('female', 'Qadın'),
    ]
    
    CATEGORY_CHOICES = [
        ('A*', 'A* Kateqoriyası'),
        ('A', 'A Kateqoriyası'),
        ('B', 'B Kateqoriyası'),
        ('C', 'C Kateqoriyası'),
        ('I ', 'I Kateqoriyası'),
    ]
    
    DEGREE_CHOICES = [
        ('VIP', 'VIP'),
        ('I', 'I Dərəcə'),
        ('II', 'II Dərəcə'),
        ('III', 'III Dərəcə'),
    ]
    
    # Basic Information
    ad = models.CharField(max_length=200, verbose_name="Ad Soyad")
    code = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        validators=[MinLengthValidator(6), MaxLengthValidator(6)],
        verbose_name="Həkim Kodu",
        help_text="6 simvollu unikal kod (avtomatik yaradılır)"
    )
    telefon = models.CharField(max_length=50, verbose_name="Telefon Nömrəsi")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='male',
        verbose_name="Cinsiyyət"
    )
    
    # Location & Organization
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
        verbose_name="Bölgə"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
        verbose_name="Şəhər"
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
        verbose_name="Klinika"
    )
    
    # Professional Information
    ixtisas = models.ForeignKey(
        Specialization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
        verbose_name="İxtisas"
    )
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default='A',
        verbose_name="Kateqoriya"
    )
    degree = models.CharField(
        max_length=3,
        choices=DEGREE_CHOICES,
        default='I',
        verbose_name="Dərəcə"
    )
    
    # Financial Information
    evvelki_borc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Əvvəlki Borc"
    )
    hesablanmish_miqdar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Hesablanmış Miqdar"
    )
    silinen_miqdar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Silinən Miqdar"
    )
    yekun_borc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Yekun Borc"
    )
    
    # Dates
    datasiya = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Datasiya")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaradılma Tarixi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yenilənmə Tarixi")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    class Meta:
        verbose_name = "Həkim"
        verbose_name_plural = "Həkimlər"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['ad']),
            models.Index(fields=['region', 'city']),
        ]

    def __str__(self):
        return f"{self.ad} ({self.code})"

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided or if it's the default value
        if not self.code or self.code == '000000':
            self.code = self.generate_unique_code()
        # Auto-calculate yekun_borc (final debt)
        self.calculate_final_debt()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        """Generate a unique 6-character code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Doctor.objects.filter(code=code).exists():
                return code

    def calculate_final_debt(self):
        """Calculate final debt: Previous Debt + Calculated Amount - Deleted Amount"""
        self.yekun_borc = self.evvelki_borc + self.hesablanmish_miqdar - self.silinen_miqdar

    @property
    def full_address(self):
        """Get full address including region, city, and clinic"""
        parts = []
        if self.clinic:
            parts.append(self.clinic.name)
        if self.city:
            parts.append(self.city.name)
        if self.region:
            parts.append(self.region.name)
        return ", ".join(parts) if parts else "Ünvan qeyd edilməyib"

    @property
    def debt_status(self):
        """Get debt status"""
        if self.yekun_borc > 0:
            return "Borclu"
        elif self.yekun_borc < 0:
            return "Artıq ödəniş"
        else:
            return "Borc yoxdur"







class DoctorPayment(models.Model):
    PAYMENT_TYPES = [
        ('avans', 'Avans'),
        ('investisiya', 'İnvestisiya'),
        ('geriqaytarma', 'Geri Qaytarma')
    ]

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor} - {self.amount} ₼"

    class Meta:
        verbose_name = "Həkim Ödənişi"
        verbose_name_plural = "Həkim Ödənişləri"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['doctor', 'region']),
        ]
