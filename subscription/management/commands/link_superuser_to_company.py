"""
Management command to link a superuser to a company
Usage: python manage.py link_superuser_to_company
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscription.models import Company, UserProfile


class Command(BaseCommand):
    help = 'Link a superuser to a company so they can access both admin and dashboard'

    def handle(self, *args, **options):
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(self.style.ERROR('No superusers found!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {superusers.count()} superuser(s):'))
        
        for idx, user in enumerate(superusers, 1):
            # Check if already has a profile
            try:
                profile = UserProfile.objects.get(user=user)
                self.stdout.write(
                    f'{idx}. {user.username} - Already linked to: {profile.company.name}'
                )
            except UserProfile.DoesNotExist:
                self.stdout.write(
                    f'{idx}. {user.username} - Not linked to any company'
                )
        
        # Get user choice
        self.stdout.write('\n' + '='*50)
        user_idx = input('Select superuser number (or press Enter to skip): ').strip()
        
        if not user_idx:
            self.stdout.write('Cancelled.')
            return
        
        try:
            user_idx = int(user_idx)
            selected_user = list(superusers)[user_idx - 1]
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR('Invalid selection!'))
            return
        
        # Get all companies
        companies = Company.objects.all()
        
        if not companies.exists():
            self.stdout.write(self.style.ERROR('No companies found! Please create a company first.'))
            return
        
        self.stdout.write(f'\n{self.style.SUCCESS("Available companies:")}')
        for idx, company in enumerate(companies, 1):
            self.stdout.write(f'{idx}. {company.name} ({company.email})')
        
        # Get company choice
        company_idx = input('\nSelect company number: ').strip()
        
        try:
            company_idx = int(company_idx)
            selected_company = list(companies)[company_idx - 1]
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR('Invalid selection!'))
            return
        
        # Check if user already has a profile
        try:
            profile = UserProfile.objects.get(user=selected_user)
            # Update existing profile
            old_company = profile.company.name
            profile.company = selected_company
            profile.role = 'owner'
            profile.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[SUCCESS] Updated {selected_user.username}\'s company '
                    f'from {old_company} to {selected_company.name}'
                )
            )
        except UserProfile.DoesNotExist:
            # Create new profile
            UserProfile.objects.create(
                user=selected_user,
                company=selected_company,
                role='owner',
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[SUCCESS] Linked {selected_user.username} to {selected_company.name} as Owner'
                )
            )
        
        self.stdout.write('\n' + self.style.SUCCESS('Done! Now you can:'))
        self.stdout.write(f'  - Access admin panel at /admin/')
        self.stdout.write(f'  - Access dashboard at /')
        self.stdout.write(f'  - Company: {selected_company.name}')

