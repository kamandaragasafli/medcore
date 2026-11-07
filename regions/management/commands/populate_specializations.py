"""
Real biznes ixtisas siyahısı (müştəri Excel/CRM kodları).
İstifadə: python manage.py populate_specializations
"""

from django.core.management.base import BaseCommand
from regions.models import Specialization


# Şəkillərdəki real siyahı: (code, name)
SPECIALIZATIONS = [
    ('CA', 'Kardioloq'),
    ('TE', 'Terapevt'),
    ('SU', 'Cərrah'),
    ('TR', 'Travmatoloq'),
    ('NE', 'Nevropatoloq'),
    ('PE', 'Pediatr'),
    ('EN', 'Endokrinoloq'),
    ('GN', 'Ginekoloq'),
    ('DE', 'Dermatoloq'),
    ('OR', 'Ortoped'),
    ('PS', 'Psixoloq'),
    ('UR', 'Uroloq'),
    ('ON', 'Onkoloq'),
    ('RE', 'Reanimatoloq'),
    ('AL', 'Allergoloq'),
    ('END', 'Endokrinoloq (əlavə)'),
    ('GA', 'Geriatriya'),
    ('LOR', 'Qulaq-Burun-Boğaz'),
    ('DV', 'Diabetoloq'),
    ('NP', 'Nevropatoloq'),
    ('AN', 'Anestezioloq'),
    ('AN/UR', 'Anesteziya/Urologiya'),
    ('BE', 'Bel Ağrısı Mütəxəssisi'),
    ('CU', 'Cərrah (əlavə)'),
    ('DZ', 'Dəri və Zöhrəvi'),
    ('EN-DIA', 'Endokrin-Diaqnostika'),
    ('EN-RN', 'Endokrin Reanimasiya'),
    ('EN-Z', 'Endokrin Zəruri'),
    ('FL', 'Flebolog'),
    ('FT', 'Fizikal Terapiya'),
    ('FZ', 'Fizioterapiya'),
    ('GAS', 'Gastroenteroloq'),
    ('GE', 'Genetika'),
    ('HE', 'Hematoloq'),
    ('IN', 'İnternist'),
    ('KA', 'Kardiak Analiz'),
    ('NEF', 'Nefrolog'),
    ('NP-C', 'Nevropatoloq-C'),
    ('OF', 'Oftalmoloq'),
    ('PE-TE', 'Pediatr Terapevt'),
    ('PED', 'Pediatr'),
    ('PU', 'Pulmonoloq'),
    ('PUL', 'Pulmonologiya'),
    ('RA', 'Revmatoloq'),
    ('RE-PE', 'Reanimasiya Pediatr'),
    ('REV', 'Revmatoid'),
    ('RV', 'Reanimasiya Vəzy'),
    ('SU-TP', 'Cərrah-Terapevt'),
    ('TP', 'Terapevtik Proses'),
    ('UR-AN', 'Urolog-Anesteziya'),
    ('URO', 'Urologiya'),
    ('URO-AND', 'Urologiya-Anesteziya'),
]


class Command(BaseCommand):
    help = 'Şəkillərdəki real ixtisasları yükləyir, digərlərini silir'

    def handle(self, *args, **options):
        import sys
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

        keep_codes = {code for code, _ in SPECIALIZATIONS}

        # Silinəcək (siyahıda olmayanlar)
        to_delete = Specialization.objects.exclude(code__in=keep_codes)
        deleted = to_delete.count()
        to_delete.delete()
        self.stdout.write(self.style.WARNING(f'Silindi: {deleted}'))

        created = 0
        updated = 0
        for code, name in SPECIALIZATIONS:
            obj, was_created = Specialization.objects.update_or_create(
                code=code,
                defaults={'name': name, 'description': ''},
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'[+] {code} — {name}'))
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nHazırdır. Yeni: {created}, yenilənən: {updated}, cəmi: {Specialization.objects.count()}'
        ))
