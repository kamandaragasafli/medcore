"""
Management command to clean default/seed data from the database.
This removes all default doctors and drugs to prepare for production use.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from doctors.models import Doctor
from drugs.models import Drug
from prescriptions.models import Prescription, PrescriptionItem
from sales.models import Sale, SaleItem
from reports.models import ArchivedReport, ArchivedReportEntry


class Command(BaseCommand):
    help = 'Clean all default/seed data (doctors, drugs, prescriptions, sales) from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: This will delete ALL data from the database!\n'
                    'This includes:\n'
                    '  - All doctors\n'
                    '  - All drugs\n'
                    '  - All prescriptions\n'
                    '  - All sales\n'
                    '  - All archived reports\n\n'
                    'To proceed, run: python manage.py clean_default_data --confirm'
                )
            )
            return

        with transaction.atomic():
            # Delete in correct order to respect foreign key constraints
            self.stdout.write('Deleting archived report entries...')
            ArchivedReportEntry.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted archived report entries'))

            self.stdout.write('Deleting archived reports...')
            ArchivedReport.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted archived reports'))

            self.stdout.write('Deleting prescription items...')
            PrescriptionItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted prescription items'))

            self.stdout.write('Deleting prescriptions...')
            Prescription.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted prescriptions'))

            self.stdout.write('Deleting sale items...')
            SaleItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted sale items'))

            self.stdout.write('Deleting sales...')
            Sale.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted sales'))

            self.stdout.write('Deleting doctors...')
            Doctor.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted doctors'))

            self.stdout.write('Deleting drugs...')
            Drug.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Deleted drugs'))

        self.stdout.write(
            self.style.SUCCESS(
                '\n✓ Successfully cleaned all default data from the database!\n'
                'The database is now ready for production use.'
            )
        )

