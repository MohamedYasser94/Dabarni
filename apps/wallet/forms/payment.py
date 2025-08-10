
from django import forms

from apps.wallet.models.Payment import PaymentGateway


class AdminPaymentGatewayForm(forms.ModelForm):
    class Meta:
        model = PaymentGateway
        fields = '__all__'