from django.db import models
import random
import string


class Region(models.Model):
    """Bölgə (Region) Model"""
    name = models.CharField(max_length=100, verbose_name="Bölgə Adı")
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        verbose_name="Bölgə Kodu",
        help_text="Unikal kod (avtomatik yaradılır)"
    )

    class Meta:
        verbose_name = "Bölgə"
        verbose_name_plural = "Bölgələr"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        """Generate a unique code for the region"""
        # Try to create code from name first (first 3-4 letters uppercase)
        if self.name:
            base_code = ''.join(c for c in self.name.upper() if c.isalnum())[:4]
            if base_code and not Region.objects.filter(code=base_code).exists():
                return base_code
        
        # If name-based code exists or name is empty, generate random code
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Region.objects.filter(code=code).exists():
                return code


class City(models.Model):
    """Şəhər (City) Model"""
    name = models.CharField(max_length=100, verbose_name="Şəhər Adı")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities', verbose_name="Bölgə")

    class Meta:
        verbose_name = "Şəhər"
        verbose_name_plural = "Şəhərlər"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class Clinic(models.Model):
    """Klinika/Xəstəxana (Clinic/Hospital) Model"""
    name = models.CharField(max_length=200, verbose_name="Klinika Adı")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='clinics', verbose_name="Bölgə")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='clinics', verbose_name="Şəhər")
    address = models.TextField(blank=True, null=True, verbose_name="Ünvan")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Əlaqə Nömrəsi")
    type = models.CharField(
        max_length=50,
        choices=[
            ('hospital', 'Xəstəxana'),
            ('clinic', 'Klinika'),
            ('polyclinic', 'Poliklinika'),
            ('medical_center', 'Tibb Mərkəzi'),
        ],
        default='clinic',
        verbose_name="Növ"
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")
    class Meta:
        verbose_name = "Klinika"
        verbose_name_plural = "Klinikalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Specialization(models.Model):
    """İxtisas (Specialization) Model"""
    name = models.CharField(max_length=200, verbose_name="İxtisas Adı")
    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Kod",
        help_text="Qısa kod (məs: TE, GN, CA, SU)"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Təsvir")

    class Meta:
        verbose_name = "İxtisas"
        verbose_name_plural = "İxtisaslar"
        ordering = ['code', 'name']

    def __str__(self):
        if self.code:
            return f"{self.code} — {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        super().save(*args, **kwargs)
