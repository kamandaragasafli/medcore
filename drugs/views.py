from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Drug
from subscription.decorators import subscription_required


@login_required
@subscription_required
def drug_list(request):
    """List all drugs with pagination"""
    drugs_list = Drug.objects.all().order_by('ad')
    
    # Pagination - 25 drugs per page
    paginator = Paginator(drugs_list, 25)
    page = request.GET.get('page', 1)
    
    try:
        drugs = paginator.page(page)
    except PageNotAnInteger:
        drugs = paginator.page(1)
    except EmptyPage:
        drugs = paginator.page(paginator.num_pages)
    
    total_drugs = drugs_list.count()
    
    context = {
        'drugs': drugs,
        'total_drugs': total_drugs,
    }
    
    return render(request, 'drugs/list.html', context)


@login_required
@subscription_required
def drug_detail(request, drug_id):
    """Display drug details"""
    drug = get_object_or_404(Drug, id=drug_id)
    
    context = {
        'drug': drug,
    }
    
    return render(request, 'drugs/detail.html', context)


@login_required
@subscription_required
def add_drug(request):
    """Add new drug - only ad, tam_ad, komissiya, qiymet"""
    if request.method == 'POST':
        try:
            ad = request.POST.get('ad', '').strip()
            tam_ad = request.POST.get('tam_ad', '').strip()
            qiymet = request.POST.get('qiymet', '').strip()
            komissiya = request.POST.get('komissiya', '').strip()
            
            if not ad or not tam_ad:
                messages.error(request, 'Ad və Tam Ad doldurulmalıdır.')
                return redirect('drugs:add')
            
            if not qiymet or not komissiya:
                messages.error(request, 'Qiymət və Komissiya doldurulmalıdır.')
                return redirect('drugs:add')
            
            Drug.objects.create(
                ad=ad,
                tam_ad=tam_ad,
                qiymet=qiymet,
                komissiya=komissiya,
            )
            messages.success(request, 'Dərman uğurla əlavə edildi!')
            return redirect('drugs:list')
            
        except Exception as e:
            messages.error(request, f'Xəta baş verdi: {str(e)}')
            return redirect('drugs:add')
    
    return render(request, 'drugs/add.html')

