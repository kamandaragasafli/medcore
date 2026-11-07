from decimal import Decimal

from django.core.management.base import BaseCommand

from doctors.models import Doctor


class Command(BaseCommand):
    help = "Set every doctor's 'evvelki_borc' field to 0."

    def handle(self, *args, **options):
        updated = 0
        for doctor in Doctor.objects.all():
            if doctor.evvelki_borc != 0:
                doctor.evvelki_borc = Decimal('0')
                doctor.save(update_fields=['evvelki_borc'])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Reset 'evvelki_borc' for {updated} doctors."))

