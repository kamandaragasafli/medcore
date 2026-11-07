from django.db import models

# Create your models here.
# reports/models.py
from django.db import models
from decimal import Decimal

from doctors.models import Doctor
from regions.models import Region


class MonthlyDoctorReport(models.Model):
    """
    Bir həkim üçün müəyyən AY + İL üzrə BAĞLANMIŞ (arxiv) hesabat.
    Bu cədvəl yalnız 'Hesabatı bağla' düyməsinə basanda doldurulur.
    """

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="monthly_reports",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monthly_doctor_reports",
    )

    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()  # 1–12

    # Dərman miqdarları JSON formatında saxlanacaq: {"Aspirin": 10, "Fensavin": 3, ...}
    drugs_data = models.JSONField(default=dict, blank=True)

    # Hesablanmış sahələr – reports səhifəsində gördüyün sahələr
    total_quantity = models.PositiveIntegerField(default=0)

    evvelki_borc = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    hesablanan = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    silinen_miqdar = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    avans = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    investisiya = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    geriqaytarma = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    datasiya = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    yekun_borc = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Aylıq Həkim Hesabatı (Bağlanmış)"
        verbose_name_plural = "Aylıq Həkim Hesabatları (Bağlanmış)"
        ordering = ["-year", "-month", "doctor__ad"]
        unique_together = (
            ("doctor", "year", "month"),
        )  # Eyni həkim üçün eyni ay yalnız bir dəfə bağlana bilər

    def __str__(self):
        return f"{self.year}-{self.month:02d} · {self.doctor.ad}"
