# api/v1/global_serializer/common_serializer.py
from rest_framework import serializers
from apps.classified.models.ticket import FcmNotification


class FcmNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FcmNotification
        fields = ['id', 'user', 'title', 'message', 'is_read', 'create_at', 'update_at']
        read_only_fields = ['id', 'create_at', 'update_at', 'user']
