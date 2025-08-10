from rest_framework import serializers

from apps.hr.models.people import *




class ClientsSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    my_absolute_url = serializers.URLField(source='get_absolute_url', read_only=True)
    class Meta:
        model = Clients
        fields = '__all__'

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


class DriverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        fields = '__all__'



