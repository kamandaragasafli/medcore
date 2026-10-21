"""
Management command to fix duplicate doctor codes
"""

from django.core.management.base import BaseCommand
from doctors.models import Doctor
import sys


class Command(BaseCommand):
    help = 'Fix duplicate doctor codes on the default database'

    def handle(self, *args, **options):
        sys.stdout.reconfigure(encoding='utf-8')

        total_fixed = 0
        doctors_to_fix = Doctor.objects.filter(code='000000') | Doctor.objects.filter(code='')

        if doctors_to_fix.exists():
            self.stdout.write(f'Found {doctors_to_fix.count()} doctors with duplicate/empty codes')
            for doctor in doctors_to_fix:
                old_code = doctor.code
                doctor.code = ''
                doctor.save()
                self.stdout.write(self.style.SUCCESS(
                    f'[OK] Fixed: {doctor.ad} ({old_code} → {doctor.code})'
                ))
                total_fixed += 1
        else:
            self.stdout.write('[OK] No duplicate codes found')

        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Fixed {total_fixed} doctor codes!'))
