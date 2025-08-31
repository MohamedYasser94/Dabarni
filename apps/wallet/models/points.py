from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.wallet.models.billing import Purchase
from helper.modelHelper import Active_Status
from user.models import UserProfile


# --- Singleton Model for Admin Settings ---
class PointSetting(models.Model):
    """
    A singleton model to hold global settings for the loyalty point system.
    Ensures that there is only one set of rules for the entire application.
    """
    money_spent_for_one_point = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10.00,
        help_text="Amount of money a user must spend to earn one point."
    )
    point_value_in_money = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.10,
        help_text="The monetary value of one point when a user redeems it."
    )
    points_expire_in_days = models.PositiveIntegerField(
        default=365,
        help_text="Number of days after which earned points expire."
    )
    min_purchase_to_earn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=20.00,
        help_text="Minimum purchase amount required to earn points."
    )

    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    code = models.CharField(unique=True, max_length=100, )
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.money_spent_for_one_point

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PointSetting-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(PointSetting, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Load the single instance of the settings, creating it if it doesn't exist."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name_plural = "Point Settings"





# --- Point Transaction Ledger ---
class PointTransaction(models.Model):
    """
    A ledger that records every change in a user's points.
    This provides a clear audit trail for all loyalty activities.
    """
    class TransactionType(models.TextChoices):
        EARN = 'EARN', 'Earned'
        REDEEM = 'REDEEM', 'Redeemed'
        EXPIRE = 'EXPIRE', 'Expired'
        ADJUST = 'ADJUST', 'Manual Adjustment'

    class PointStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        REDEEMED = 'REDEEMED', 'Redeemed'
        EXPIRED = 'EXPIRED', 'Expired'

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='point_transactions'
    )
    points = models.IntegerField(help_text="Number of points for this transaction (can be negative for redemptions/expirations).")
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=PointStatus.choices, default=PointStatus.ACTIVE)
    related_purchase = models.ForeignKey(
        Purchase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The purchase that generated or used these points."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when these specific points will expire (only for 'EARN' type)."
    )

    def __str__(self):
        return f"{self.user_profile.user.email} - {self.transaction_type}: {self.points} points"

    def save(self, *args, **kwargs):
        # Automatically calculate the expiry date for new 'EARN' transactions
        if self.pk is None and self.transaction_type == self.TransactionType.EARN:
            settings = PointSetting.load()
            self.expiry_date = timezone.now() + timedelta(days=settings.points_expire_in_days)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']



