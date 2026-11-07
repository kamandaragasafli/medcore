"""
Management command to update subscription plans with new doctor limits and prices
"""

from django.core.management.base import BaseCommand
from subscription.models import SubscriptionPlan, Company
import sys


class Command(BaseCommand):
    help = 'Update subscription plans with new doctor limits and prices'

    def handle(self, *args, **options):
        sys.stdout.reconfigure(encoding='utf-8')
        
        self.stdout.write(self.style.WARNING('Updating subscription plans...\n'))
        
        # Update Basic Plan
        basic_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='basic',
            defaults={
                'name': 'Əsas Plan',
                'description': '500 həkimə qədər - Kiçik klinikalar üçün',
                'price_monthly': 150.00,
                'price_yearly': 1500.00,
            }
        )
        basic_plan.name = 'Əsas Plan'
        basic_plan.description = '500 həkimə qədər - Kiçik klinikalar üçün'
        basic_plan.price_monthly = 150.00
        basic_plan.price_yearly = 1500.00
        basic_plan.max_users = 10
        basic_plan.max_doctors = 500
        basic_plan.max_patients = 5000
        basic_plan.max_storage_gb = 10
        basic_plan.features = [
            'Həkim İdarəetməsi',
            'Xəstə Qeydiyyatı',
            'Satış Modulu',
            'Ödəniş Sistemi',
            'Əsas Hesabatlar',
            'Email Dəstəyi',
        ]
        basic_plan.is_active = True
        basic_plan.is_popular = False
        basic_plan.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ {basic_plan.name}: {basic_plan.max_doctors} həkim, {basic_plan.price_monthly} AZN/ay'
        ))
        
        # Update Professional Plan
        professional_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='professional',
            defaults={
                'name': 'Professional Plan',
                'description': '1500 həkimə qədər - Orta və böyük klinikalar üçün',
                'price_monthly': 200.00,
                'price_yearly': 2000.00,
            }
        )
        professional_plan.name = 'Professional Plan'
        professional_plan.description = '1500 həkimə qədər - Orta və böyük klinikalar üçün'
        professional_plan.price_monthly = 200.00
        professional_plan.price_yearly = 2000.00
        professional_plan.max_users = 25
        professional_plan.max_doctors = 1500
        professional_plan.max_patients = 15000
        professional_plan.max_storage_gb = 50
        professional_plan.features = [
            'Həkim İdarəetməsi',
            'Xəstə Qeydiyyatı',
            'Satış Modulu',
            'Ödəniş Sistemi',
            'Təkmil Hesabatlar',
            'Analytics Dashboard',
            'SMS Bildirişləri',
            'Telefon Dəstəyi',
            'Prioritet Dəstək',
        ]
        professional_plan.is_active = True
        professional_plan.is_popular = True  # Most popular
        professional_plan.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ {professional_plan.name}: {professional_plan.max_doctors} həkim, {professional_plan.price_monthly} AZN/ay'
        ))
        
        # Update Enterprise Plan
        enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
            plan_type='enterprise',
            defaults={
                'name': 'Enterprise Plan',
                'description': '2000 həkimə qədər - Böyük tibb şəbəkələri üçün',
                'price_monthly': 250.00,
                'price_yearly': 2500.00,
            }
        )
        enterprise_plan.name = 'Enterprise Plan'
        enterprise_plan.description = '2000 həkimə qədər - Böyük tibb şəbəkələri üçün'
        enterprise_plan.price_monthly = 250.00
        enterprise_plan.price_yearly = 2500.00
        enterprise_plan.max_users = 100
        enterprise_plan.max_doctors = 2000
        enterprise_plan.max_patients = 50000
        enterprise_plan.max_storage_gb = 200
        enterprise_plan.features = [
            'Həkim İdarəetməsi',
            'Xəstə Qeydiyyatı',
            'Satış Modulu',
            'Ödəniş Sistemi',
            'Təkmil Hesabatlar',
            'Analytics Dashboard',
            'SMS Bildirişləri',
            'Çoxsaylı Filiallar',
            'API Access',
            'Custom Integrations',
            '24/7 Telefon Dəstəyi',
            'Dedicated Account Manager',
            'Training & Onboarding',
        ]
        enterprise_plan.is_active = True
        enterprise_plan.is_popular = False
        enterprise_plan.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ {enterprise_plan.name}: {enterprise_plan.max_doctors} həkim, {enterprise_plan.price_monthly} AZN/ay'
        ))
        
        self.stdout.write(self.style.WARNING('\nUpdating company limits...\n'))
        
        # Update existing companies to match their subscription plan limits
        companies = Company.objects.all()
        
        for company in companies:
            subscription = company.active_subscription
            if subscription and subscription.plan:
                old_limit = company.max_doctors
                company.max_doctors = subscription.plan.max_doctors
                company.max_users = subscription.plan.max_users
                company.max_patients = subscription.plan.max_patients
                company.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f'✓ {company.name}: {old_limit} → {company.max_doctors} həkim limiti'
                ))
            else:
                # No active subscription, set to basic plan limits
                company.max_doctors = 500
                company.max_users = 10
                company.max_patients = 5000
                company.save()
                
                self.stdout.write(self.style.WARNING(
                    f'⚠ {company.name}: Aktiv abunə yoxdur, əsas plan limitləri tətbiq edildi'
                ))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Bütün planlar uğurla yeniləndi!'))
        self.stdout.write('\nYeni Plan Limitləri:')
        self.stdout.write('  Əsas Plan:        500 həkim  - 150 AZN/ay')
        self.stdout.write('  Professional:    1500 həkim - 200 AZN/ay')
        self.stdout.write('  Enterprise:      2000 həkim - 250 AZN/ay')

