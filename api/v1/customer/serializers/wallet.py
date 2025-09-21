# api/v1/customer/serializers/wallet.py
from decimal import Decimal
from rest_framework import serializers
from apps.wallet.models.models import Wallet, WalletMoney, WalletLocked


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "user", "wallet_locked", "user_nuc", "code", "amount", "status", "create_at", "update_at"]
        read_only_fields = ["id", "user", "wallet_locked", "code", "status", "create_at", "update_at"]


class WalletMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletMoney
        fields = [
            "id", "wallet", "user", "actual_balance",
            "reversed_balance", "earning", "paid", "due",
            "receive", "send", "code", "create_at", "update_at"
        ]
        read_only_fields = ["id", "wallet", "user", "actual_balance", "reversed_balance", "earning",
                            "paid", "due", "receive", "send", "code", "create_at", "update_at"]


class CreateWalletSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, default="123456", allow_blank=True)
    user_nuc = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(required=False, max_digits=50, decimal_places=2, default=Decimal("0.00"))

    def validate_amount(self, value):
        if value is None:
            return Decimal("0.00")
        if value < Decimal("0.00"):
            raise serializers.ValidationError("amount must be >= 0")
        return value


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=50, decimal_places=2)

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("amount must be greater than 0")
        return value


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=50, decimal_places=2)

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("amount must be greater than 0")
        return value
