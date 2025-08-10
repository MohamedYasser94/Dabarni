from rest_framework import serializers

from core.models.core import *




class ConfigSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigSetting
        fields = '__all__'

class CommonProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonProfile
        fields = '__all__'


class CommonTranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonTranslate
        fields = '__all__'


class CommonMediaFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonMediaFiles
        fields = '__all__'