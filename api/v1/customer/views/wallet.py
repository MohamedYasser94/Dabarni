from rest_framework import serializers

from apps.wallet.models.Payment import PaymentGateway, PaymentGatewaySetting
from apps.wallet.models.billing import Purchase


class PaymentGatewaySerializer(serializers.ModelSerializer):
    # This is the magic part. We create a custom field for 'settings'.
    settings = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGateway
        fields = [
            'id',
            'name',
            'gateway_name',
            'image',
            'status',
            'settings'  # Include our custom settings field
        ]

    def get_settings(self, obj):
        """
        This method fetches all settings for a gateway, takes the first one,
        and serializes it. If no settings exist, it returns an empty object.
        """
        # In Django, the reverse relation is named 'paymentgatewaysetting_set' by default
        # but you have a related_name='settings' on your ForeignKey in the model,
        # so we can access it via obj.settings
        # If your ForeignKey from PaymentGatewaySetting to PaymentGateway is named 'gateway',
        # the reverse relationship is gateway.paymentgatewaysetting_set.all()
        # Let's assume the related_name is not set and use the default.

        # Check if the related name is set in your PaymentGatewaySetting model.
        # If the ForeignKey to PaymentGateway is `gateway`, the default reverse name is `paymentgatewaysetting_set`.
        # However, it's better practice to add related_name='settings' to the ForeignKey in PaymentGatewaySetting model.
        # Let's assume for now the default name is used.
        # If you add `related_name='settings'` to the ForeignKey in PaymentGatewaySetting,
        # you can simply use `setting = obj.settings.first()`

        setting = PaymentGatewaySetting.objects.filter(gateway=obj).first()

        if setting:
            # If a setting object exists, serialize it
            return PaymentGatewaySettingSerializer(setting).data

        # If no settings are found, return an empty map, as Flutter expects
        return {}


class PaymentGatewaySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewaySetting
        # We only need these specific fields in the Flutter app
        fields = ['setting_key', 'setting_secret']


class PurchaseSerializer(serializers.Serializer):
    class Meta:
        model =Purchase
        fields = '__all__'
