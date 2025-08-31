# accounts/serializers.py
from rest_framework import serializers
from user.models import User ,UserAddress

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'otp', 'otp_expiry']

####################### Requts ################ 

class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField()
    access_level = serializers.ChoiceField(choices=['Client', 'Provider'])

class ConfirmOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            "id",
            "label",
            "latitude",
            "longitude",
            "address",
            "building_name",
            "floor",
            "apartment_number",
            "property_type",
            "note",
        ]
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()