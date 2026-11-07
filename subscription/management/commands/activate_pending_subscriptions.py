"""
Management command to activate pending subscriptions where contract is agreed
Usage: python manage.py activate_pending_subscriptions
"""
from django.core.management.base import BaseCommand
from subscription.models import Subscription, ContractAgreement


class Command(BaseCommand):
    help = 'Activate pending subscriptions where contract is agreed'

    def handle(self, *args, **options):
        self.stdout.write('Activating pending subscriptions with agreed contracts...\n')
        
        pending_subs = Subscription.objects.filter(status='pending')
        activated_count = 0
        
        for subscription in pending_subs:
            # Check if contract is agreed for this company
            contracts = ContractAgreement.objects.filter(
                company=subscription.company,
                agreed=True
            )
            
            if contracts.exists():
                subscription.status = 'active'
                subscription.save()
                activated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Activated subscription for {subscription.company.name} '
                        f'(Plan: {subscription.plan.name})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Skipping {subscription.company.name} - no agreed contract found'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Activated {activated_count} subscription(s)'
            )
        )
