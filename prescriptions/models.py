from django.db import models
from doctors.models import Doctor
from drugs.models import Drug
from regions.models import Region


class Prescription(models.Model):
    """
    Prescription/Recipe Model
    Stores prescription information with doctor and drugs
    """
    
    # Region Information
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name='Bölgə',
        null=True,
        blank=True
    )

    # Doctor Information
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name='Həkim'
    )
    
    # Date Information
    date = models.DateField(verbose_name='Tarix')
    
    # Patient Information (optional)
    patient_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Xəstə Adı'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Qeyd'
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaradılıb')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yenilənib')
    
    class Meta:
        verbose_name = 'Resept'
        verbose_name_plural = 'Reseptlər'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['doctor']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        region_name = self.region.name if self.region else 'Bölgə'
        doctor_name = self.doctor.ad if self.doctor else 'Həkim'
        return f"{region_name} - {doctor_name} - {self.date}"
    
    @property
    def total_amount(self):
        """Calculate total amount for all drugs in prescription"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def drug_count(self):
        """Count of drugs in prescription"""
        return self.items.count()


class PrescriptionItem(models.Model):
    """
    Individual drug items in a prescription
    """
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Resept'
    )
    
    drug = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        verbose_name='Dərman'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Say'
    )
    
    # Price at time of prescription (in case drug price changes later)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Vahid Qiyməti'
    )
    
    # Dosage instructions
    dosage = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Dozaj'
    )
    
    # Duration
    duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Müddət'
    )
    
    class Meta:
        verbose_name = 'Resept Elementi'
        verbose_name_plural = 'Resept Elementləri'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.drug.ad} x {self.quantity}"
    
    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        # Set unit price from drug if not set
        if not self.unit_price:
            self.unit_price = self.drug.yekun_qiymet
        super().save(*args, **kwargs)

