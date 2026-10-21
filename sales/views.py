from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from datetime import datetime

from subscription.decorators import subscription_required
from .models import Sale, SaleItem
from regions.models import Region
from drugs.models import Drug

MONTH_CHOICES = [
    (1, "Yanvar"),
    (2, "Fevral"),
    (3, "Mart"),
    (4, "Aprel"),
    (5, "May"),
    (6, "İyun"),
    (7, "İyul"),
    (8, "Avqust"),
    (9, "Sentyabr"),
    (10, "Oktyabr"),
    (11, "Noyabr"),
    (12, "Dekabr"),
]

def monthly_sales(request):
    region_id = (request.GET.get("region") or "").strip()
    month = (request.GET.get("month") or "").strip()

    # Base queryset for SaleItem (çünki dərmanlar burdadır)
    items = SaleItem.objects.select_related("sale", "drug", "sale__region")

    # Region filter
    if region_id:
        items = items.filter(sale__region_id=region_id)

    # Month filter
    if month:
        try:
            month_int = int(month)
            if 1 <= month_int <= 12:
                items = items.filter(sale__date__month=month_int)
            else:
                month = ""
        except ValueError:
            month = ""

    drugs = Drug.objects.all()
    regions_qs = Region.objects.all()

    if region_id:
        regions_qs = regions_qs.filter(id=region_id)

    table_data = []
    summary_total = 0

    for region in regions_qs:
        row = {
            "region": region,
            "drugs": {},
            "total": 0,
        }

        for drug in drugs:
            qty = (
                items.filter(sale__region=region, drug=drug)
                .aggregate(total=Sum("quantity"))["total"]
                or 0
            )

            row["drugs"][drug.ad] = qty
            row["total"] += qty

        summary_total += row["total"]
        table_data.append(row)

    table_info_parts = []

    # Table info (region + month shown above table)
    if month:
        month_label = next(
            (label for value, label in MONTH_CHOICES if str(value) == month),
            "Seçilmiş ay",
        )
        table_info_parts.append(month_label)
    else:
        table_info_parts.append("Bütün aylar")

    if region_id and regions_qs.exists():
        table_info_parts.append(regions_qs.first().name)
    else:
        table_info_parts.append("Bütün bölgələr")

    table_info_parts.append(f"Ümumi: {summary_total} satış")

    context = {
        "regions": Region.objects.all(),
        "drugs": drugs,
        "data": table_data,
        "months": MONTH_CHOICES,
        "filters": {
            "region": region_id,
            "month": month,
        },
        "table_info": " - ".join(table_info_parts),
        "summary_total": summary_total,
    }

    return render(request, "sales/sales.html", context)


@login_required
@subscription_required
def add_sale(request):

    if request.method == "POST":
        try:
            with transaction.atomic():

                region_id = request.POST.get("region_id")
                date_str = request.POST.get("date")

                if not region_id or not date_str:
                    messages.error(request, "Bölgə və tarix seçilməlidir.")
                    return redirect("sales:add")

                try:
                    sale_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Tarix formatı yanlışdır.")
                    return redirect("sales:add")

                region = Region.objects.get(id=region_id)

                # Create Sale
                sale = Sale.objects.create(
                    region=region,
                    date=sale_date
                )

                # Collect drug quantities
                selected_drugs = []
                for key, value in request.POST.items():
                    if key.startswith("drug_"):
                        drug_id = int(key.split("_")[1])
                        qty = int(value) if value else 0
                        if qty > 0:
                            selected_drugs.append((drug_id, qty))

                if not selected_drugs:
                    messages.error(request, "Ən azı 1 dərman seçilməlidir.")
                    return redirect("sales:add")

                drug_ids = [d[0] for d in selected_drugs]
                drugs_map = {d.id: d for d in Drug.objects.filter(id__in=drug_ids)}

                # Add Sale Items
                for drug_id, qty in selected_drugs:
                    drug = drugs_map.get(drug_id)
                    SaleItem.objects.create(
                        sale=sale,
                        drug=drug,
                        quantity=qty,
                        unit_price=drug.qiymet
                    )

                messages.success(request, "Satış uğurla əlavə edildi!")
                return redirect("sales:add")

        except Exception as e:
            messages.error(request, f"Xəta baş verdi: {str(e)}")
            return redirect("sales:add")

    # GET
    regions = Region.objects.all().order_by("name")
    drugs = Drug.objects.filter(is_active=True).order_by("ad")

    return render(request, "sales/add.html", {
        "regions": regions,
        "drugs": drugs
    })


@login_required
@subscription_required
def sale_list(request):
    """List individual sales with edit link"""
    region_id = (request.GET.get("region") or "").strip()
    month = (request.GET.get("month") or "").strip()

    sales = Sale.objects.select_related("region").prefetch_related("items__drug").order_by("-date")

    if region_id:
        sales = sales.filter(region_id=region_id)
    if month:
        try:
            month_int = int(month)
            if 1 <= month_int <= 12:
                sales = sales.filter(date__month=month_int)
        except ValueError:
            pass

    context = {
        "sales": sales,
        "regions": Region.objects.all().order_by("name"),
        "months": MONTH_CHOICES,
        "filters": {"region": region_id, "month": month},
    }
    return render(request, "sales/sale_list.html", context)


@login_required
@subscription_required
def edit_sale(request, sale_id):
    """Edit existing sale"""
    sale = get_object_or_404(Sale, id=sale_id)
    sale.items.prefetch_related("drug")

    if request.method == "POST":
        try:
            with transaction.atomic():
                region_id = request.POST.get("region_id")
                date_str = request.POST.get("date")
                if not region_id or not date_str:
                    messages.error(request, "Bölgə və tarix seçilməlidir.")
                    return redirect("sales:edit", sale_id=sale_id)

                try:
                    sale_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Tarix formatı yanlışdır.")
                    return redirect("sales:edit", sale_id=sale_id)

                region = Region.objects.get(id=region_id)
                sale.region = region
                sale.date = sale_date
                sale.save()

                # Collect drug quantities from form
                selected_drugs = []
                for key, value in request.POST.items():
                    if key.startswith("drug_"):
                        drug_id = int(key.split("_")[1])
                        qty = int(value) if value else 0
                        if qty > 0:
                            selected_drugs.append((drug_id, qty))

                if not selected_drugs:
                    messages.error(request, "Ən azı 1 dərman seçilməlidir.")
                    return redirect("sales:edit", sale_id=sale_id)

                drug_ids = [d[0] for d in selected_drugs]
                drugs_map = {d.id: d for d in Drug.objects.filter(id__in=drug_ids)}

                # Remove old items and create new
                sale.items.all().delete()
                for drug_id, qty in selected_drugs:
                    drug = drugs_map.get(drug_id)
                    if drug:
                        SaleItem.objects.create(
                            sale=sale,
                            drug=drug,
                            quantity=qty,
                            unit_price=drug.qiymet,
                        )

                messages.success(request, "Satış uğurla yeniləndi!")
                return redirect("sales:sale_list")
        except Exception as e:
            messages.error(request, f"Xəta baş verdi: {str(e)}")
            return redirect("sales:edit", sale_id=sale_id)

    # GET: show form with current sale data
    regions = Region.objects.all().order_by("name")
    drugs = Drug.objects.filter(is_active=True).order_by("ad")
    items_by_drug = {item.drug_id: item.quantity for item in sale.items.select_related("drug")}

    return render(request, "sales/edit.html", {
        "sale": sale,
        "regions": regions,
        "drugs": drugs,
        "items_by_drug": items_by_drug,
    })
