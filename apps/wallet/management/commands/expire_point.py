from django.core.management.base import BaseCommand
from django.utils import timezone

from django.db import transaction

from apps.wallet.models.points import PointTransaction
from user.models import UserProfile


class Command(BaseCommand):
    help = 'Expires loyalty points that are past their expiry date.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting point expiration process...")

        # Find all 'EARN' transactions that are past their expiry date and are still active
        expired_transactions = PointTransaction.objects.filter(
            transaction_type=PointTransaction.TransactionType.EARN,
            status=PointTransaction.PointStatus.ACTIVE,
            expiry_date__lte=timezone.now()
        )

        if not expired_transactions.exists():
            self.stdout.write(self.style.SUCCESS("No points to expire today."))
            return

        points_to_expire_by_user = {}

        # Group points to be expired by user
        for trans in expired_transactions:
            user_profile_id = trans.user_profile.id
            if user_profile_id not in points_to_expire_by_user:
                points_to_expire_by_user[user_profile_id] = 0
            points_to_expire_by_user[user_profile_id] += trans.points

        # Process expirations for each user
        for user_profile_id, total_points_to_expire in points_to_expire_by_user.items():
            try:
                profile = UserProfile.objects.get(pk=user_profile_id)

                # Deduct points from the user's current balance
                profile.current_points = max(0, profile.current_points - total_points_to_expire)
                profile.save()

                # Create a single expiration transaction for this user
                PointTransaction.objects.create(
                    user_profile=profile,
                    points=-total_points_to_expire,  # Record as a negative value
                    transaction_type=PointTransaction.TransactionType.EXPIRE,
                    status=PointTransaction.PointStatus.EXPIRED  # This is a final state
                )

                self.stdout.write(
                    f"Expired {total_points_to_expire} points for user {profile.user.username}"
                )

            except UserProfile.DoesNotExist:
                self.stderr.write(f"UserProfile with id {user_profile_id} not found. Skipping.")

        # Mark the original 'EARN' transactions as expired
        expired_count = expired_transactions.update(status=PointTransaction.PointStatus.EXPIRED)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully expired {expired_count} point transactions.")
        )



