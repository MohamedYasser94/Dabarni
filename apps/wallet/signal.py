from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.wallet.models.billing import Purchase
from apps.wallet.models.points import PointTransaction, PointSetting
from user.models import UserProfile


# --- Signal to Award Points Automatically ---
@receiver(post_save, sender=Purchase)
def award_points_on_purchase(sender, instance, created, **kwargs):
    """
    A signal that automatically awards loyalty points to a user
    when their purchase is marked as completed and paid.
    """
    # Ensure the purchase is complete and paid to award points
    if instance.purchase_status == 'Completed' and instance.payment_status == 'Paid':
        # Check if points have already been awarded for this purchase
        if not PointTransaction.objects.filter(related_purchase=instance).exists():
            settings = PointSetting.load()
            user = instance.owner # Assuming 'owner' is the user who made the purchase

            # Check if purchase amount meets the minimum requirement
            if user and instance.amount >= settings.min_purchase_to_earn:
                # Calculate points earned
                points_earned = int(instance.amount / settings.money_spent_for_one_point)

                if points_earned > 0:
                    # Get or create the user's loyalty profile
                    profile, created = UserProfile.objects.get_or_create(user=user)

                    # Create a new point transaction record
                    PointTransaction.objects.create(
                        user_profile=profile,
                        points=points_earned,
                        transaction_type=PointTransaction.TransactionType.EARN,
                        related_purchase=instance,
                        status=PointTransaction.PointStatus.ACTIVE
                    )

                    # Update the user's profile with the new points
                    profile.current_points += points_earned
                    profile.lifetime_points += points_earned
                    profile.save()