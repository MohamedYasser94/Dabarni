from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from user.models import UserProfile
from api.v1.customer.serializers.profile_serializer import UserProfileSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser


class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(tags=["Profile"], responses=UserProfileSerializer)
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    @extend_schema(tags=["Profile"], request=UserProfileSerializer,
        responses=UserProfileSerializer)
    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "تم تحديث البيانات بنجاح", "data": serializer.data})
        return Response(serializer.errors, status=400)
