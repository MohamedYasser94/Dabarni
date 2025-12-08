from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api.v1.provider.serializers.classified import MobileNotificationSerializer
from core.models.notifications import MobileNotification

class UserNotificationListView(generics.ListAPIView):
    serializer_class = MobileNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MobileNotification.objects.filter(recipient=self.request.user).order_by('-created')