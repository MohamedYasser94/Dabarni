from rest_framework import serializers

from core.models.localization import *


class AdminLanguageSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Language
        fields = "__all__"


class AdminCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"



class AdminCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


