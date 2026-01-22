from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from apps.wallet.models.models import PendingBalanceTransfer

class Command(BaseCommand):
    help = 'Process pending balance transfers from reversed_balance to actual_balance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be transferred without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        pending_transfers = PendingBalanceTransfer.objects.filter(
            status='Pending',
            transfer_at__lte=now
        ).select_related('wallet_money', 'user')
        
        if not pending_transfers.exists():
            self.stdout.write(self.style.SUCCESS('No pending transfers to process.'))
            return

        self.stdout.write(f'Found {pending_transfers.count()} pending transfer(s) to process.')
        processed_count = 0
        error_count = 0
        for transfer in pending_transfers:
            try:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Would transfer {transfer.amount} to '
                        f'actual_balance for user {transfer.user.id} '
                        f'(job_id: {transfer.job_id})'
                    )
                    continue

                with transaction.atomic():
                    wallet_money = transfer.wallet_money
                    amount = transfer.amount
                    current_reversed = wallet_money.reversed_balance or Decimal('0')
                    current_actual = wallet_money.actual_balance or Decimal('0')

                    if current_reversed < amount:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Insufficient reversed_balance for transfer {transfer.id}. '
                                f'Expected: {amount}, Available: {current_reversed}. '
                                f'Transferring available amount.'
                            )
                        )
                        amount = current_reversed
                    
                    wallet_money.reversed_balance = current_reversed - amount
                    wallet_money.actual_balance = current_actual + amount
                    wallet_money.save()
                    transfer.status = 'Completed'
                    transfer.transferred_at = now
                    transfer.notes = f'Transferred {amount} successfully'
                    transfer.save()
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Transferred {amount} to actual_balance for user {transfer.user.id}'
                        )
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing transfer {transfer.id}: {str(e)}'
                    )
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Completed: {processed_count} transfers processed, {error_count} errors.'
                )
            )
