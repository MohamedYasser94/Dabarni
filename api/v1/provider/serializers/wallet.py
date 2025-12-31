import logging
from rest_framework import serializers

from apps.wallet.models.payment import PaymentGateway, Payment, BankAccount, Banks
from apps.wallet.models.billing import Invoice, Billing
from apps.wallet.models.models import WalletMoney
from apps.wallet.models.transaction import MoneyTransaction, PayoutRequest

logger = logging.getLogger(__name__)


class ProviderInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "billing", "amount", "status", "created_at", "updated_at"]


class ProviderBillingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = ["id", "provider", "total_amount", "status", "created_at"]


class ProviderWalletMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletMoney
        fields = ["id", "user", "actual_balance", "reversed_balance","code", "create_at", "update_at"]


class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ["id", "name", "logo", "is_active"]


class ProviderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "amount", "currency", "status", "gateway", "created_at"]


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = ["id", "name", "swift_code", "country"]


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "user",
            "bank_name",
            "account_number",
            "iban",
            "swift_code",
            "default_account",
            "created_at",
        ]


class ProviderMoneyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyTransaction
        fields = ["id", "wallet", "amount", "transaction_type", "status", "created_at"]
        
class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        # قمنا بتغيير provider إلى user ليطابق الموديل
        fields = ["id", "user", "amount", "status", "created_at", "processed_at"]
        read_only_fields = ["id", "user", "status", "created_at", "processed_at"]