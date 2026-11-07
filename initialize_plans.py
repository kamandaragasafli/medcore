"""
Script to initialize subscription plans in the database
Run this after migrations: python initialize_plans.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from subscription.models import SubscriptionPlan

def create_plans():
    print("Creating subscription plans...")
    
    # Delete existing plans (optional)
    # SubscriptionPlan.objects.all().delete()
    
    # Basic Plan
    basic, created = SubscriptionPlan.objects.get_or_create(
        plan_type='basic',
        defaults={
            'name': 'Basic',
            'description': 'Perfect for small clinics and practices',
            'price_monthly': 29.99,
            'price_yearly': 299.99,
            'max_users': 5,
            'max_doctors': 3,
            'max_patients': 100,
            'max_storage_gb': 5,
            'features': [
                'Up to 5 users',
                '3 doctors',
                '100 patients',
                '5GB storage',
                'Basic reports',
                'Email support',
                'Mobile app access'
            ],
            'is_active': True,
            'is_popular': False
        }
    )
    print(f"[OK] Basic plan {'created' if created else 'already exists'}")
    
    # Professional Plan
    pro, created = SubscriptionPlan.objects.get_or_create(
        plan_type='professional',
        defaults={
            'name': 'Professional',
            'description': 'For growing medical practices',
            'price_monthly': 79.99,
            'price_yearly': 799.99,
            'max_users': 20,
            'max_doctors': 10,
            'max_patients': 500,
            'max_storage_gb': 50,
            'features': [
                'Up to 20 users',
                '10 doctors',
                '500 patients',
                '50GB storage',
                'Advanced reports',
                'Priority support',
                'API access',
                'Custom branding',
                'Multiple locations'
            ],
            'is_active': True,
            'is_popular': True
        }
    )
    print(f"[OK] Professional plan {'created' if created else 'already exists'}")
    
    # Enterprise Plan
    enterprise, created = SubscriptionPlan.objects.get_or_create(
        plan_type='enterprise',
        defaults={
            'name': 'Enterprise',
            'description': 'For hospitals and large organizations',
            'price_monthly': 199.99,
            'price_yearly': 1999.99,
            'max_users': 100,
            'max_doctors': 50,
            'max_patients': 5000,
            'max_storage_gb': 500,
            'features': [
                'Unlimited users',
                '50+ doctors',
                '5000+ patients',
                '500GB storage',
                'Enterprise reports',
                '24/7 premium support',
                'Full API access',
                'White label option',
                'Dedicated account manager',
                'SLA guarantee',
                'Custom integrations',
                'On-premise option'
            ],
            'is_active': True,
            'is_popular': False
        }
    )
    print(f"[OK] Enterprise plan {'created' if created else 'already exists'}")
    
    print("\n[SUCCESS] All subscription plans initialized successfully!")
    print(f"Total plans: {SubscriptionPlan.objects.count()}")

if __name__ == '__main__':
    create_plans()

