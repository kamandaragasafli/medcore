"""
Simple helper command to create 10 pill medicines (tablets)
with prices between 1–5 AZN.

This runs for the CURRENT database (single-tenant context).
Use tenant routing if needed before calling.
"""

import random
from decimal import Decimal

from django.core.management.base import BaseCommand

from drugs.models import Drug


class Command(BaseCommand):
    help = 'Create 10 tablet-form drugs priced between 1 and 5 AZN (name and barcode auto-generated).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating 10 pill medicines (tablets) with price 1–5 AZN...'))

        created_count = 0

        for i in range(1, 11):
            # Random price between 1.00 and 5.00
            price = Decimal(random.randint(100, 500)) / Decimal('100')

            # Simple fixed commission, e.g. 0.50 AZN
            commission = Decimal('0.50')

            base_name = f"Test Pill {i}"
            full_name = f"{base_name} 100mg"

            # Ensure unique barcode; if collision, try a few times
            barcode = None
            for attempt in range(5):
                candidate = f"PILL{i:02d}{random.randint(1000, 9999)}"
                if not Drug.objects.filter(barkod=candidate).exists():
                    barcode = candidate
                    break

            drug = Drug.objects.create(
                ad=base_name,
                tam_ad=full_name,
                qiymet=price,
                komissiya=commission,
                buraxilis_formasi='tablet',
                dozaj="100mg",
                barkod=barcode,
                is_active=True,
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [+] Created drug: {drug.ad} | price={drug.qiymet} AZN | barcode={drug.barkod}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Successfully created {created_count} pill medicines (tablets).")
        )


