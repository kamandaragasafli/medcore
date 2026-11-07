"""
Management command to update existing company owners to be staff members
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from subscription.models import UserProfile


class Command(BaseCommand):
    help = 'Update existing company owners to be staff members'

    def handle(self, *args, **options):
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        
        # Get all owner profiles
        owner_profiles = UserProfile.objects.filter(role='owner')
        
        if not owner_profiles.exists():
            self.stdout.write(self.style.WARNING('No company owners found'))
            return
        
        self.stdout.write(f'Found {owner_profiles.count()} company owners')
        
        updated_count = 0
        for profile in owner_profiles:
            user = profile.user
            if not user.is_staff:
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  [OK] Updated: {user.username} ({profile.company.name})'))
                updated_count += 1
            else:
                self.stdout.write(f'  [SKIP] Already staff: {user.username}')
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Updated {updated_count} users to staff'))

