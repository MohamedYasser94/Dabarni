from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models.chat import  Message

User = get_user_model()





class AdminMessageSerializer(serializers.ModelSerializer)    :
    user_online = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = "__all__"

    def get_user_online(self, obj):
        return obj.user.is_online
    def get_user_email(self, obj):
        return obj.user.email