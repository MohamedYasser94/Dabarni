import logging

from rest_framework import serializers

from apps.wallet.models.Payment import PaymentGateway, Payment, BankAccount, Banks
from apps.wallet.models.billing import Invoice, Billing
from apps.wallet.models.models import WalletMoney
from apps.wallet.models.transaction import MoneyTransaction

logger = logging.getLogger(__name__)


class ProviderInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class ProviderBillingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = '__all__'


class ProviderWalletMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletMoney
        fields = '__all__'


class PaymentGatewaySerializer(serializers.Serializer):
    class Meta:
        model = PaymentGateway
        fields = '__all__'


class ProviderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class BankSerializer(serializers.Serializer):
    class Meta:
        model = Banks
        fields = '__all__'

class BankAccountSerializer(serializers.Serializer):
    class Meta:
        model = BankAccount
        fields = '__all__'


class ProviderMoneyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyTransaction
        fields = '__all__'