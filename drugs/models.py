from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Drug(models.Model):
    """
    Dərman (Drug/Medicine) Model
    Komissiya — manatla ifadə olunan sabit məbləğdir (faiz deyil!)
    """

    RELEASE_FORM_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Kapsul'),
        ('syrup', 'Sirop'),
        ('injection', 'İnyeksiya'),
        ('cream', 'Krem'),
        ('ointment', 'Məlhəm'),
        ('drops', 'Damcı'),
        ('spray', 'Sprey'),
        ('powder', 'Toz'),
        ('solution', 'Məhlul'),
    ]

    # Basic Information
    ad = models.CharField(max_length=200, verbose_name="Ad", help_text="Qısa ad")
    tam_ad = models.CharField(max_length=500, verbose_name="Tam Ad", help_text="Dərmanın tam adı")

    # Financial Information
    qiymet = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Qiymət",
        help_text="Qiymət (AZN)"
    )

    # ✔ DƏYİŞDİ — komissiya artıq MİQDARdır, faiz deyil
    komissiya = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Komissiya",
        help_text="Komissiya məbləği (AZN olaraq)"
    )

    # Drug Details
    buraxilis_formasi = models.CharField(
        max_length=50,
        choices=RELEASE_FORM_CHOICES,
        default='tablet',
        verbose_name="Buraxılış Forması"
    )

    dozaj = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Dozaj"
    )

    barkod = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Barkod"
    )

    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaradılıb")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yenilənib")

    class Meta:
        verbose_name = "Dərman"
        verbose_name_plural = "Dərmanlar"
        ordering = ['ad']
        indexes = [
            models.Index(fields=['ad']),
            models.Index(fields=['buraxilis_formasi']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.ad} - {self.komissiya}"

    

