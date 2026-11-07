import random

from django.core.management.base import BaseCommand
from django.db import transaction

from doctors.models import Doctor
from regions.models import Region


FIRST_NAMES = [
    "Əli", "Aygün", "Rəşid", "Nigar", "Kamran",
    "Fidan", "Murad", "Lalə", "Tural", "Sabina",
]

LAST_NAMES = [
    "Hüseynov", "Məmmədova", "İbrahimov", "Quliyeva", "Əliyev",
    "Rəhimova", "Mehdiyev", "Talıbova", "İsmayılov", "Cəfərova",
]

DEGREES = ['VIP', 'I', 'II', 'III']
GENDERS = ['male', 'female']


class Command(BaseCommand):
    help = "Delete all doctors and create 10 per region with zeroed financial data."

    def handle(self, *args, **options):
        regions = Region.objects.all()
        if not regions.exists():
            self.stdout.write(self.style.ERROR("No regions found. Abort."))
            return

        with transaction.atomic():
            deleted = Doctor.objects.count()
            Doctor.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} doctors.")

            created = 0
            for region in regions:
                for index in range(10):
                    first = random.choice(FIRST_NAMES)
                    last = random.choice(LAST_NAMES)
                    gender = random.choice(GENDERS)
                    degree = DEGREES[index % len(DEGREES)]

                    doctor = Doctor.objects.create(
                        ad=f"{first} {last}",
                        telefon=f"+99450{random.randint(1000000, 9999999)}",
                        region=region,
                        gender=gender,
                        ixtisas=None,
                        category='A',
                        degree=degree,
                        evvelki_borc=0,
                        hesablanmish_miqdar=0,
                        silinen_miqdar=0,
                        yekun_borc=0,
                    )
                    created += 1
            self.stdout.write(self.style.SUCCESS(f"Created {created} doctors (10 per region)."))

