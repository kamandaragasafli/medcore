"""
Management command to create:
- Region: "Baku Region 6"
- One hospital in that region
- 30 doctors assigned to that region and hospital
"""

from django.core.management.base import BaseCommand

from regions.models import Region, City, Clinic
from doctors.models import Doctor


class Command(BaseCommand):
    help = 'Create "Baku Region 6", a hospital in that region, and 30 doctors assigned to it.'

    REGION_NAME = "Baku Region 6"
    REGION_CODE = "BAK6"
    CITY_NAME = "Baku Region 6 City"
    CLINIC_NAME = "Baku Region 6 Hospital"

    def handle(self, *args, **options):
        import sys

        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

        created_count = self._create_region_hospital_and_doctors()
        self.stdout.write(
            self.style.SUCCESS(
                f"\n[SUCCESS] Finished creating Baku Region 6 data. Doctors created: {created_count}"
            )
        )

    def _create_region_hospital_and_doctors(self) -> int:
        """
        Create the region, city, hospital clinic, and up to 30 doctors.
        Returns the number of doctors created.
        """

        # 1) Create/get Region
        region, region_created = Region.objects.get_or_create(
            code=self.REGION_CODE,
            defaults={"name": self.REGION_NAME},
        )

        if region_created:
            self.stdout.write(
                self.style.SUCCESS(f'  [+] Created region: "{region.name}" ({region.code})')
            )
        else:
            self.stdout.write(
                f'  [=] Region already exists: "{region.name}" ({region.code})'
            )

        # 2) Create/get City for that region
        city, city_created = City.objects.get_or_create(
            name=self.CITY_NAME,
            region=region,
        )

        if city_created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [+] Created city: "{city.name}" for region "{region.name}"'
                )
            )
        else:
            self.stdout.write(
                f'  [=] City already exists: "{city.name}" for region "{region.name}"'
            )

        # 3) Create/get Hospital clinic in that region/city
        clinic_defaults = {
            "region": region,
            "city": city,
            "address": "Baku Region 6 Main Street",
            "phone": "+994 12 600 0006",
            "type": "hospital",
        }

        clinic, clinic_created = Clinic.objects.get_or_create(
            name=self.CLINIC_NAME,
            defaults=clinic_defaults,
        )

        # If clinic already exists but is missing some fields (older data),
        # make sure critical relations are aligned with this region/city.
        if not clinic_created:
            updated = False
            if clinic.region != region:
                clinic.region = region
                updated = True
            if clinic.city != city:
                clinic.city = city
                updated = True
            if clinic.type != "hospital":
                clinic.type = "hospital"
                updated = True
            if updated:
                clinic.save()

        if clinic_created:
            self.stdout.write(
                self.style.SUCCESS(f'  [+] Created hospital: "{clinic.name}"')
            )
        else:
            self.stdout.write(f'  [=] Hospital already exists: "{clinic.name}"')

        # 4) Create up to 30 doctors assigned to this region & hospital
        existing_in_region = Doctor.objects.filter(region=region).count()
        remaining = max(0, 30 - existing_in_region)

        if remaining == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"  [=] Region already has {existing_in_region} doctors. No new doctors created."
                )
            )
            return 0

        self.stdout.write(
            self.style.WARNING(
                f"  Creating {remaining} doctors for region '{region.name}' (currently {existing_in_region}/30)..."
            )
        )

        doctors_created = 0

        for i in range(remaining):
            sequence_number = existing_in_region + i + 1
            name = f"Baku Region 6 Doctor {sequence_number}"

            # Simple deterministic phone pattern
            phone = f"+994 50 600 {sequence_number:04d}"

            Doctor.objects.create(
                ad=name,
                telefon=phone,
                region=region,
                city=city,
                clinic=clinic,
            )

            doctors_created += 1

        return doctors_created


