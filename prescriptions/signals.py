from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from prescriptions.models import PrescriptionItem
from doctors.services.financial_calculator import recalculate_doctor_financials


@receiver(post_save, sender=PrescriptionItem)
def prescription_item_saved(sender, instance, **kwargs):
    """Resept əlavə/dəyişdirildikdə həmin reseptin ayı üçün hesablama et"""
    doctor_id = instance.prescription.doctor_id
    prescription_date = instance.prescription.date
    if doctor_id and prescription_date:
        recalculate_doctor_financials(
            doctor_ids=[doctor_id],
            month=prescription_date.month,
            year=prescription_date.year
        )


@receiver(post_delete, sender=PrescriptionItem)
def prescription_item_deleted(sender, instance, **kwargs):
    """Resept silindikdə həmin reseptin ayı üçün hesablama et"""
    doctor_id = instance.prescription.doctor_id
    prescription_date = instance.prescription.date
    if doctor_id and prescription_date:
        recalculate_doctor_financials(
            doctor_ids=[doctor_id],
            month=prescription_date.month,
            year=prescription_date.year
        )

