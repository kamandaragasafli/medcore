"""
Management command to populate test data:
- 5 regions with cities and clinics
- 10 doctors per region (50 total)
- 10 drugs
"""

from django.core.management.base import BaseCommand
from regions.models import Region, City, Clinic, Specialization
from doctors.models import Doctor
from drugs.models import Drug


class Command(BaseCommand):
    help = 'Populate test data: 5 regions, 10 doctors per region, 10 drugs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Populating test data...'))
        
        # Create 5 Regions with Cities and Clinics
        regions_data = [
            {
                'name': 'Bakı',
                'code': 'BAK',
                'city': 'Bakı',
                'clinic': 'Bakı Mərkəzi Klinika',
                'address': 'Nəsimi rayonu, 28 May küç. 15',
                'phone': '+994 12 555 0000'
            },
            {
                'name': 'Gəncə',
                'code': 'GAN',
                'city': 'Gəncə',
                'clinic': 'Gəncə Şəhər Xəstəxanası',
                'address': 'Nizami küç. 45',
                'phone': '+994 22 555 0001'
            },
            {
                'name': 'Sumqayıt',
                'code': 'SMQ',
                'city': 'Sumqayıt',
                'clinic': 'Sumqayıt Tibb Mərkəzi',
                'address': '1-ci mikrorayon',
                'phone': '+994 18 555 0002'
            },
            {
                'name': 'Mingəçevir',
                'code': 'MIN',
                'city': 'Mingəçevir',
                'clinic': 'Mingəçevir Regional Xəstəxana',
                'address': 'Heydər Əliyev prospekti',
                'phone': '+994 25 555 0003'
            },
            {
                'name': 'Şəki',
                'code': 'SAK',
                'city': 'Şəki',
                'clinic': 'Şəki Şəhər Xəstəxanası',
                'address': 'Mərkəzi küç. 20',
                'phone': '+994 24 555 0004'
            },
        ]
        
        regions = {}
        for data in regions_data:
            # Create Region
            region, created = Region.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            regions[data['code']] = region
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created region: {region.name}'))
            else:
                self.stdout.write(f'  Region exists: {region.name}')
            
            # Create City
            city, created = City.objects.get_or_create(
                name=data['city'],
                region=region,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created city: {city.name}'))
            else:
                self.stdout.write(f'  City exists: {city.name}')
            
            # Create Clinic
            clinic, created = Clinic.objects.get_or_create(
                name=data['clinic'],
                defaults={
                    'region': region,
                    'city': city,
                    'address': data['address'],
                    'phone': data['phone'],
                    'type': 'hospital'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created clinic: {clinic.name}'))
            else:
                self.stdout.write(f'  Clinic exists: {clinic.name}')
        
        # Create Specializations if not exists
        specializations_data = [
            {'name': 'Terapevt', 'code': 'THER'},
            {'name': 'Kardioloq', 'code': 'CARD'},
            {'name': 'Nevroloq', 'code': 'NEUR'},
            {'name': 'Pediatr', 'code': 'PEDI'},
            {'name': 'Cərrah', 'code': 'SURG'},
        ]
        
        specializations = {}
        for data in specializations_data:
            spec, created = Specialization.objects.get_or_create(
                code=data['code'],
                defaults={'name': data['name']}
            )
            specializations[data['code']] = spec
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created specialization: {spec.name}'))
        
        # Create 10 doctors per region
        doctors_created = 0
        for region_code, region in regions.items():
            city = City.objects.filter(region=region).first()
            clinic = Clinic.objects.filter(region=region).first()
            
            existing_count = Doctor.objects.filter(region=region).count()
            remaining = max(0, 10 - existing_count)
            
            if remaining == 0:
                self.stdout.write(f'  Region {region.name} already has {existing_count} doctors')
                continue
            
            self.stdout.write(f'  Creating {remaining} doctors for {region.name}...')
            
            for i in range(remaining):
                sequence_number = existing_count + i + 1
                name = f"{region.name} Həkim {sequence_number}"
                phone = f"+994 50 {region_code}{sequence_number:04d}"
                
                # Random specialization
                import random
                spec_code = random.choice(list(specializations.keys()))
                specialization = specializations[spec_code]
                
                Doctor.objects.create(
                    ad=name,
                    telefon=phone,
                    region=region,
                    city=city,
                    clinic=clinic,
                    ixtisas=specialization,
                    degree='müəllim',
                    category='birinci',
                    gender='male' if sequence_number % 2 == 0 else 'female'
                )
                doctors_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {doctors_created} doctors total'))
        
        # Create 10 Drugs
        drugs_data = [
            {'name': 'Parasetamol', 'tam_ad': 'Parasetamol 500mg Tablet', 'qiymet': 2.50},
            {'name': 'İbuprofen', 'tam_ad': 'İbuprofen 400mg Tablet', 'qiymet': 3.00},
            {'name': 'Amoksiklav', 'tam_ad': 'Amoksiklav 625mg Tablet', 'qiymet': 8.50},
            {'name': 'Azitromisin', 'tam_ad': 'Azitromisin 500mg Tablet', 'qiymet': 12.00},
            {'name': 'Omeprazol', 'tam_ad': 'Omeprazol 20mg Kapsul', 'qiymet': 4.50},
            {'name': 'Diklofenak', 'tam_ad': 'Diklofenak 75mg Tablet', 'qiymet': 3.50},
            {'name': 'Sitramon', 'tam_ad': 'Sitramon Tablet', 'qiymet': 1.50},
            {'name': 'Vitamin C', 'tam_ad': 'Vitamin C 500mg Tablet', 'qiymet': 2.00},
            {'name': 'Kalsium', 'tam_ad': 'Kalsium D3 Tablet', 'qiymet': 5.00},
            {'name': 'Aspirin', 'tam_ad': 'Aspirin 100mg Tablet', 'qiymet': 2.80},
        ]
        
        drugs_created = 0
        for data in drugs_data:
            drug, created = Drug.objects.get_or_create(
                ad=data['name'],
                defaults={
                    'tam_ad': data['tam_ad'],
                    'qiymet': data['qiymet'],
                    'komissiya': 0.50,
                    'buraxilis_formasi': 'tablet',
                    'dozaj': '500mg',
                    'barkod': f"DRUG{drugs_created + 1:04d}",
                    'is_active': True
                }
            )
            if created:
                drugs_created += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created drug: {drug.ad}'))
            else:
                self.stdout.write(f'  Drug exists: {drug.ad}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Successfully populated test data!'))
        self.stdout.write(self.style.WARNING('\nSummary:'))
        self.stdout.write(f'  Regions: {Region.objects.count()}')
        self.stdout.write(f'  Cities: {City.objects.count()}')
        self.stdout.write(f'  Clinics: {Clinic.objects.count()}')
        self.stdout.write(f'  Doctors: {Doctor.objects.count()}')
        self.stdout.write(f'  Drugs: {Drug.objects.count()}')
