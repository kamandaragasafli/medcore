"""
Management command to populate initial regions, cities, clinics, and specializations
Run this for each tenant database or for the current company
"""

from django.core.management.base import BaseCommand
from regions.models import Region, City, Clinic, Specialization


class Command(BaseCommand):
    help = 'Populate initial regions, cities, clinics, and specializations data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Populating regions data...'))
        
        # Create Regions (Bölgələr)
        regions_data = [
            {'name': 'Bakı', 'code': 'BAK'},
            {'name': 'Gəncə', 'code': 'GAN'},
            {'name': 'Sumqayıt', 'code': 'SMQ'},
            {'name': 'Mingəçevir', 'code': 'MIN'},
            {'name': 'Abşeron', 'code': 'ABS'},
            {'name': 'Ağcabədi', 'code': 'AGC'},
            {'name': 'Ağdam', 'code': 'AGD'},
            {'name': 'Ağdaş', 'code': 'AGS'},
            {'name': 'Ağstafa', 'code': 'AGT'},
            {'name': 'Ağsu', 'code': 'AGU'},
        ]
        
        regions = {}
        for data in regions_data:
            region, created = Region.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            regions[data['code']] = region
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created region: {region.name}'))
            else:
                self.stdout.write(f'  Region exists: {region.name}')
        
        # Create Cities (Şəhərlər)
        cities_data = [
            {'name': 'Bakı', 'region': 'BAK'},
            {'name': 'Sumqayıt', 'region': 'SMQ'},
            {'name': 'Gəncə', 'region': 'GAN'},
            {'name': 'Mingəçevir', 'region': 'MIN'},
            {'name': 'Xırdalan', 'region': 'ABS'},
            {'name': 'Ağcabədi', 'region': 'AGC'},
        ]
        
        cities = {}
        for data in cities_data:
            city, created = City.objects.get_or_create(
                name=data['name'],
                region=regions[data['region']],
            )
            cities[data['name']] = city
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created city: {city.name}'))
            else:
                self.stdout.write(f'  City exists: {city.name}')
        
        # Create Clinics (Klinikalar)
        clinics_data = [
            {
                'name': 'Bakı Mərkəzi Klinika',
                'region': 'BAK',
                'city': 'Bakı',
                'address': 'Nəsimi rayonu, 28 May küç. 15',
                'phone': '+994 12 555 0000',
                'type': 'clinic'
            },
            {
                'name': 'Gəncə Şəhər Xəstəxanası',
                'region': 'GAN',
                'city': 'Gəncə',
                'address': 'Nizami küç. 45',
                'phone': '+994 22 555 0001',
                'type': 'hospital'
            },
            {
                'name': 'Sumqayıt Tibb Mərkəzi',
                'region': 'SMQ',
                'city': 'Sumqayıt',
                'address': '1-ci mikrorayon',
                'phone': '+994 18 555 0002',
                'type': 'medical_center'
            },
        ]
        
        for data in clinics_data:
            clinic, created = Clinic.objects.get_or_create(
                name=data['name'],
                defaults={
                    'region': regions[data['region']],
                    'city': cities[data['city']],
                    'address': data['address'],
                    'phone': data['phone'],
                    'type': data['type'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created clinic: {clinic.name}'))
            else:
                self.stdout.write(f'  Clinic exists: {clinic.name}')
        
        # Create Specializations (İxtisaslar)
        specializations_data = [
            {'name': 'Terapevt', 'code': 'THER'},
            {'name': 'Kardioloq', 'code': 'CARD'},
            {'name': 'Nevroloq', 'code': 'NEUR'},
            {'name': 'Pediatr', 'code': 'PEDI'},
            {'name': 'Cərrah', 'code': 'SURG'},
            {'name': 'Ortoped', 'code': 'ORTH'},
            {'name': 'Dermatoloq', 'code': 'DERM'},
            {'name': 'Oftalmolоq', 'code': 'OPHT'},
            {'name': 'Stomatoloq', 'code': 'DENT'},
            {'name': 'Ginekoloq', 'code': 'GYNE'},
        ]
        
        for data in specializations_data:
            spec, created = Specialization.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created specialization: {spec.name}'))
            else:
                self.stdout.write(f'  Specialization exists: {spec.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully populated regions data!'))
        self.stdout.write(self.style.WARNING('\nSummary:'))
        self.stdout.write(f'  Regions: {Region.objects.count()}')
        self.stdout.write(f'  Cities: {City.objects.count()}')
        self.stdout.write(f'  Clinics: {Clinic.objects.count()}')
        self.stdout.write(f'  Specializations: {Specialization.objects.count()}')

