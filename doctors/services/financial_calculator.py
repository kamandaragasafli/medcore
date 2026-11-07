from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Q

from doctors.models import Doctor
from prescriptions.models import PrescriptionItem
from sales.models import SaleItem
from drugs.models import Drug


DEGREE_FACTORS = {
    'VIP': Decimal('1.00'),
    'I': Decimal('0.90'),
    'II': Decimal('0.65'),
    'III': Decimal('0.40'),
}


def recalculate_doctor_financials(doctor_ids=None, region_ids=None, month=None, year=None):
    """
    Recalculate doctor financial metrics for a specific month/year.
    doctor_ids: list of doctor IDs that must be recalculated
    region_ids: list of region IDs whose doctors need recalculation (e.g. after sales change)
    month: filter prescriptions/sales by this month (1-12). If None, uses all data.
    year: filter prescriptions/sales by this year. If None, uses all data.
    """
    doctor_ids = set(doctor_ids or [])

    if region_ids:
        region_doctors = Doctor.objects.filter(region_id__in=region_ids).values_list('id', flat=True)
        doctor_ids.update(region_doctors)

    if not doctor_ids:
        print("[FINANCIAL CALC] No doctors to process.")
        return

    doctors = list(
        Doctor.objects.filter(id__in=doctor_ids)
        .select_related('region')
    )

    if not doctors:
        print("[FINANCIAL CALC] Doctor queryset is empty. Abort.")
        return

    doctor_map = {doctor.id: doctor for doctor in doctors}
    doctor_region_map = {doctor.id: doctor.region_id for doctor in doctors}
    region_ids = {rid for rid in doctor_region_map.values() if rid}

    degree_map = {
        doctor.id: DEGREE_FACTORS.get(doctor.degree, Decimal('1.00'))
        for doctor in doctors
    }

    drug_commission_map = {
    drug.id: Decimal(str(drug.komissiya))
    for drug in Drug.objects.filter(is_active=True)
    }


    doctor_weighted = defaultdict(lambda: defaultdict(Decimal))
    region_weighted = defaultdict(Decimal)  # key: (region_id, drug_id)

    if region_ids:
        prescription_filter = Q(prescription__region_id__in=region_ids) | Q(prescription__doctor__region_id__in=region_ids)
    else:
        prescription_filter = Q(prescription__doctor_id__in=doctor_ids)

    prescription_items = (
        PrescriptionItem.objects
        .filter(prescription_filter)
        .select_related('prescription__doctor', 'prescription__region', 'drug')
    )
    
    # Ay və il filtri (tets.txt kimi)
    if month:
        prescription_items = prescription_items.filter(prescription__date__month=month)
    if year:
        prescription_items = prescription_items.filter(prescription__date__year=year)

    for item in prescription_items:
        doctor = item.prescription.doctor
        if not doctor:
            continue

        region_id = item.prescription.region_id or doctor.region_id
        if not region_id:
            continue

        factor = degree_map.get(doctor.id, Decimal('1.00'))
        weighted_value = Decimal(item.quantity) * factor

        region_weighted[(region_id, item.drug_id)] += weighted_value

        if doctor.id in doctor_ids:
            doctor_weighted[doctor.id][item.drug_id] += weighted_value
            print("Doctor:", doctor.id, "Drug:", item.drug_id, "Prescription:", item.quantity, "Weighted:", weighted_value)

    region_sales = defaultdict(Decimal)
    if region_ids:
        sale_items = (
            SaleItem.objects
            .filter(sale__region_id__in=region_ids)
            .select_related('sale__region', 'drug')
        )
        
        # Ay və il filtri (satış tarixi üzrə)
        if month:
            sale_items = sale_items.filter(sale__date__month=month)
        if year:
            sale_items = sale_items.filter(sale__date__year=year)
        
        for sale_item in sale_items:
            region_sales[(sale_item.sale.region_id, sale_item.drug_id)] += Decimal(sale_item.quantity)

    effectiveness_map = {}
    for key, weighted_sum in region_weighted.items():
        sales_sum = region_sales.get(key, Decimal('0'))
        if weighted_sum > 0:
            ratio = sales_sum / weighted_sum
        else:
            ratio = Decimal('0')
        effectiveness_map[key] = ratio
        print("Drug:", key[1], "Weighted Total:", weighted_sum, "Sales:", sales_sum, "Effectiveness:", ratio)

    for doctor in doctors:
        print("=== CALCULATION STARTED FOR DOCTOR", doctor.id, "===")
        if not doctor.region_id:
            print("Doctor has no region; skipping effectiveness calculations.")
            doctor.hesablanmish_miqdar = Decimal('0')
            doctor.silinen_miqdar = Decimal('0')
            doctor.yekun_borc = doctor.evvelki_borc
            doctor.save(update_fields=[
                "hesablanmish_miqdar",
                "silinen_miqdar",
                "yekun_borc"
            ])
            print("=== CALCULATION FINISHED ===")
            continue

        doctor_effective_total = Decimal('0')
        doctor_commission_total = Decimal('0')

        weighted_totals = sum(doctor_weighted.get(doctor.id, {}).values(), Decimal('0'))
        print("Weighted Prescriptions:", weighted_totals)

        for drug_id, weighted_qty in doctor_weighted.get(doctor.id, {}).items():
            ratio = effectiveness_map.get((doctor.region_id, drug_id), Decimal('0'))
            print("Effectiveness Ratio (Region:", doctor.region_id, "Drug:", drug_id, "):", ratio)
            doctor_effective_value = (weighted_qty * ratio).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            doctor_effective_total += doctor_effective_value
            print("Doctor Effective Value:", doctor_effective_value)

            commission_rate = drug_commission_map.get(drug_id, Decimal('0'))
            commission_amount = (commission_rate * doctor_effective_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  
            doctor_commission_total += commission_amount
            print("Commission for Drug:", drug_id, "=", commission_amount)

        doctor.hesablanmish_miqdar = doctor_effective_total
        doctor.silinen_miqdar = doctor_commission_total
        doctor.yekun_borc = doctor.evvelki_borc + doctor_effective_total - doctor_commission_total

        doctor.save(update_fields=[
            "hesablanmish_miqdar",
            "silinen_miqdar",
            "yekun_borc"
        ])

        print("UPDATED DOCTOR VALUES:", doctor.id,
              "Effective:", doctor_effective_total,
              "Commission:", doctor_commission_total,
              "Final Debt:", doctor.yekun_borc)
        print("Effective Total:", doctor_effective_total)
        print("Commission Total:", doctor_commission_total)
        print("Final Debt:", doctor.yekun_borc)
        print("=== CALCULATION FINISHED ===")

