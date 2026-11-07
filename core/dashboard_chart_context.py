"""
Professional dashboard üçün əlavə qrafik datası.

İstifadə (view-da, mövcud context-i qurandan sonra):

    from .dashboard_chart_context import build_chart_context
    context.update(build_chart_context(prescriptions_qs, sales_qs, items_qs))

Parametrlər artıq istifadəçiyə/təşkilata görə filtrlənmiş queryset-lər olmalıdır
(mövcud kodunuzda necə filtrləyirsinizsə, eyni qaydada).

"ADJUST" yazılan sahə adları təxmindir, öz modellərinizə uyğunlaşdırın.
"""
import json
from datetime import timedelta

from django.db.models import Count, Sum, F
from django.db.models.functions import ExtractWeekDay, TruncMonth
from django.utils import timezone

AZ_MONTHS = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'İyn',
             'İyl', 'Avq', 'Sen', 'Okt', 'Noy', 'Dek']


def _last_months(n=12):
    d = timezone.localdate().replace(day=1)
    months = []
    for _ in range(n):
        months.append(d)
        d = (d - timedelta(days=1)).replace(day=1)
    return months[::-1]


def _pct(cur, prev):
    cur, prev = float(cur or 0), float(prev or 0)
    if prev == 0:
        return None
    return round((cur - prev) / prev * 100, 1)


def build_chart_context(prescriptions, sales, prescription_items=None):
    today = timezone.localdate()
    months = _last_months(12)
    first = months[0]

    # ---- Aylıq satış sayı və gəlir ----
    from django.db.models import F
    from sales.models import SaleItem
    
    sale_rows = (
        sales.filter(date__gte=first)                      # ADJUST: tarix sahəsi
        .annotate(m=TruncMonth('date'))
        .values('m')
        .annotate(c=Count('id'))
    )
    sale_map = {(r['m'].year, r['m'].month): r for r in sale_rows}

    monthly_sales = [sale_map.get((m.year, m.month), {}).get('c', 0) for m in months]
    
    # Calculate revenue from SaleItem
    revenue_rows = (
        SaleItem.objects.filter(sale__date__gte=first)
        .annotate(m=TruncMonth('sale__date'))
        .values('m')
        .annotate(r=Sum(F('quantity') * F('unit_price')))
    )
    revenue_map = {(r['m'].year, r['m'].month): r for r in revenue_rows}
    monthly_revenue = [float(revenue_map.get((m.year, m.month), {}).get('r') or 0) for m in months]

    # ---- Aylıq qeydiyyat (sparkline üçün) ----
    rx_rows = (
        prescriptions.filter(date__gte=first)              # ADJUST
        .annotate(m=TruncMonth('date'))
        .values('m')
        .annotate(c=Count('id'))
    )
    rx_map = {(r['m'].year, r['m'].month): r['c'] for r in rx_rows}
    monthly_rx = [rx_map.get((m.year, m.month), 0) for m in months]

    # ---- Bölgələr ----
    region_rows = (
        prescriptions.values('region__name')               # ADJUST
        .annotate(c=Count('id'))
        .order_by('-c')[:6]
    )
    region_labels = [r['region__name'] or 'Digər' for r in region_rows]
    region_data = [r['c'] for r in region_rows]

    # ---- Həftənin günləri (Bazar ertəsi birinci) ----
    weekday = [0] * 7
    for r in (prescriptions.annotate(wd=ExtractWeekDay('date'))   # ADJUST
              .values('wd').annotate(c=Count('id'))):
        # Django: 1 = Bazar, 2 = Bazar ertəsi ... 7 = Şənbə
        weekday[(r['wd'] + 5) % 7] = r['c']

    # ---- Aktiv / deaktiv ----
    active = prescriptions.filter(is_active=True).count()       # ADJUST
    inactive = prescriptions.filter(is_active=False).count()

    # ---- Dərmanlar ----
    drug_labels, drug_data = [], []
    if prescription_items is not None:
        rows = (
            prescription_items.values('drug__ad')              # ADJUST: drug__ad not drug__name
            .annotate(c=Count('id'))
            .order_by('-c')[:7]
        )
        drug_labels = [r['drug__ad'] or '-' for r in rows]
        drug_data = [r['c'] for r in rows]

    # ---- Son 30 gün vs əvvəlki 30 gün ----
    d30, d60 = today - timedelta(days=30), today - timedelta(days=60)
    rx_cur = prescriptions.filter(date__gte=d30).count()
    rx_prev = prescriptions.filter(date__gte=d60, date__lt=d30).count()
    s_cur = sales.filter(date__gte=d30)
    s_prev = sales.filter(date__gte=d60, date__lt=d30)

    # Calculate revenue from SaleItem for growth
    from django.db.models import F
    revenue_cur = SaleItem.objects.filter(sale__date__gte=d30).aggregate(
        t=Sum(F('quantity') * F('unit_price'))
    )['t'] or 0
    revenue_prev = SaleItem.objects.filter(sale__date__gte=d60, sale__date__lt=d30).aggregate(
        t=Sum(F('quantity') * F('unit_price'))
    )['t'] or 0

    return {
        'monthly_labels': json.dumps([AZ_MONTHS[m.month - 1] for m in months]),
        'monthly_sales_data': json.dumps(monthly_sales),
        'monthly_revenue_data': json.dumps(monthly_revenue),
        'monthly_prescription_data': json.dumps(monthly_rx),
        'region_labels': json.dumps(region_labels),
        'region_data': json.dumps(region_data),
        'weekday_data': json.dumps(weekday),
        'drug_labels': json.dumps(drug_labels),
        'drug_data': json.dumps(drug_data),
        'active_prescriptions': active,
        'inactive_prescriptions': inactive,
        'prescriptions_growth': _pct(rx_cur, rx_prev),
        'sales_growth': _pct(s_cur.count(), s_prev.count()),
        'revenue_growth': _pct(revenue_cur, revenue_prev),
    }
