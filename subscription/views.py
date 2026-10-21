from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Company, SubscriptionPlan, Subscription, UserProfile, ContractAgreement
from datetime import timedelta


def subscription_plans(request):
    """Display subscription plans/pricing page"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    context = {
        'plans': plans,
    }
    return render(request, 'subscription/plans.html', context)


@transaction.atomic
def register_company(request):
    """Company registration - single company per deployment"""
    if request.method == 'POST':
        # Get form data
        company_name = request.POST.get('company_name')
        company_phone = request.POST.get('company_phone', '')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        plan_id = request.POST.get('plan_id') or request.GET.get('plan')
        
        # Validation
        if not company_name or not company_phone or not username or not password or not password_confirm:
            messages.error(request, 'Bütün sahələr doldurulmalıdır!')
            return redirect('subscription:register')
        
        if password != password_confirm:
            messages.error(request, 'Parollar uyğun gəlmir!')
            return redirect('subscription:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'İstifadəçi adı artıq mövcuddur!')
            return redirect('subscription:register')
        
        if not plan_id:
            messages.error(request, 'Paket seçilməyib! Zəhmət olmasa paket seçin.')
            return redirect('subscription:plans')
        
        try:
            # Get selected plan
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Seçilmiş paket tapılmadı!')
            return redirect('subscription:plans')
        
        try:
            if Company.objects.exists():
                messages.error(
                    request,
                    'Bu sistemdə artıq şirkət qeydiyyatdan keçib. '
                    'Yeni müştəri üçün ayrı nüsxə quraşdırın.'
                )
                return redirect('subscription:plans')

            slug = slugify(company_name) or 'company'
            base_slug = slug
            counter = 1
            while Company.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            email = f"{username}@medadmin.local"

            company = Company.objects.create(
                name=company_name,
                slug=slug,
                email=email,
                phone=company_phone,
                is_active=True
            )

            # Create User (Company Owner)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='',
                last_name='',
                # Company owners should NOT access Django admin directly.
                # Only superadmins (master admin) can use the admin panel.
                is_staff=False
            )
            
            # Create User Profile
            UserProfile.objects.create(
                user=user,
                company=company,
                role='owner',
                phone=company_phone,
                is_active=True
            )
            
            # Create Subscription with selected plan
            subscription = Subscription.objects.create(
                company=company,
                plan=plan,
                status='pending',  # Pending until contract is agreed
                billing_cycle='monthly',
                start_date=timezone.now(),
                amount=plan.price_monthly,
                auto_renew=True
            )
            
            # Update company limits based on plan
            company.max_users = plan.max_users
            company.max_doctors = plan.max_doctors
            company.max_patients = plan.max_patients
            company.save()
            
            # Log the user in
            login(request, user)
            
            # Redirect to contract agreement page (təsdiqləmə)
            return redirect('subscription:contract')
            
        except Exception as e:
            messages.error(request, f'Xəta baş verdi: {str(e)}')
            return redirect('subscription:register')
    
    # GET request - show registration form
    plan_id = request.GET.get('plan')
    plan = None
    if plan_id:
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'Seçilmiş paket tapılmadı!')
            return redirect('subscription:plans')
    
    if not plan:
        messages.info(request, 'Zəhmət olmasa əvvəlcə paket seçin.')
        return redirect('subscription:plans')
    
    context = {
        'plan': plan,
        'plan_id': plan.id,
    }
    return render(request, 'subscription/register.html', context)


def subscription_success(request):
    """Success page after subscription"""
    return render(request, 'subscription/success.html')


def contract_view(request):
    """Display contract and handle agreement"""
    if not request.user.is_authenticated:
        return redirect('core:login')
    
    # Get user's company
    try:
        user_profile = request.user.profile
        company = user_profile.company
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please contact support.')
        return redirect('core:login')
    
    # Check if already agreed
    contract, created = ContractAgreement.objects.get_or_create(
        company=company,
        user=request.user,
        defaults={
            'contract_version': '1.0',
            'contract_text': get_default_contract_text(),
        }
    )
    
    if contract.agreed:
        # Already agreed, activate subscription and redirect to dashboard
        subscription = company.subscriptions.filter(
            status__in=['pending', 'active']
        ).order_by('-created_at').first()
        
        if subscription and subscription.status == 'pending':
            subscription.status = 'active'
            subscription.save()
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        agreed = request.POST.get('agreed') == 'on'
        
        if agreed:
            contract.agreed = True
            contract.agreed_at = timezone.now()
            contract.ip_address = get_client_ip(request)
            contract.save()
            
            # Activate subscription (get pending subscription if exists)
            subscription = company.subscriptions.filter(
                status__in=['pending', 'active']
            ).order_by('-created_at').first()
            
            if subscription and subscription.status == 'pending':
                subscription.status = 'active'
                subscription.save()
            
            messages.success(request, 'Müqavilə təsdiqləndi! Xoş gəlmisiniz!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Müqaviləni qəbul etməlisiniz.')
    
    context = {
        'contract': contract,
        'company': company,
    }
    
    return render(request, 'subscription/contract.html', context)


def get_default_contract_text():
    """Get default contract text"""
    return """
XİDMƏT ŞƏRTLƏRİ VƏ İSTİFADƏ MÜQAVILƏSİ

1. ÜMUMİ ŞƏRTLƏR
Bu müqavilə MedAdmin xidmətlərindən istifadə ilə bağlı şərtləri müəyyən edir.

2. XİDMƏTLƏRDƏN İSTİFADƏ
- Xidmətlərdən yalnız qanuni məqsədlər üçün istifadə edə bilərsiniz
- Hesab məlumatlarınızın təhlükəsizliyindən siz məsulsunuz
- Digər istifadəçilərin hüquqlarını pozmaq qadağandır

3. ÖDƏNİŞLƏR
- Abunəlik ödənişləri avtomatik yenilənir
- Ləğv etmək istəsəniz, abunəlik bitməzdən ən azı 7 gün əvvəl bildirməlisiniz
- Geri qaytarma siyasəti: İlk 30 gün ərzində tam geri qaytarma mümkündür

4. MƏLUMATLARIN MƏXDİYYƏTİ
- Bütün məlumatlar şifrələnmiş formada saxlanılır
- Məlumatlarınızı üçüncü tərəflərlə paylaşmırıq
- GDPR və yerli qanunvericiliyə riayət edirik

5. MƏHDUDİYYƏTLƏR
- Xidmətlərdən sui-istifadə qadağandır
- Sistemə zərərli kod yükləmək qadağandır
- Digər istifadəçilərin məlumatlarına yetkisiz giriş qadağandır

6. LƏĞV ETMƏ
- İstənilən vaxt abunəliyi ləğv edə bilərsiniz
- Ləğv etdikdən sonra məlumatlarınız 30 gün saxlanılır

7. DƏYİŞİKLİKLƏR
- Bu müqaviləni istənilən vaxt yeniləyə bilərik
- Dəyişikliklər haqqında sizə bildiriş göndəriləcək

Bu şərtlərlə razılaşırsınız?
"""


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

