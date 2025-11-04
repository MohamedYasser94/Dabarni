from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.v1.global_serializer.auth_serializer import UserAddressSerializer
from user.models import UserAddress, UserProfile
from api.v1.customer.serializers.profile_serializer import UserProfileSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from user.models import User
from api.v1.global_serializer.auth_serializer import RegisterSerializer , ConfirmOTPSerializer , UserAddressSerializer ,LogoutSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from api.v1.response import success_response, error_response

class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(tags=["Customer Profile"], responses=UserProfileSerializer)
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    @extend_schema(tags=["Customer Profile"], request=UserProfileSerializer,
        responses=UserProfileSerializer)
    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        print("Request data ------------------",request.data)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True,context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "تم تحديث البيانات بنجاح", "data": serializer.data})
        return Response(serializer.errors, status=400)



#----------------------------

@extend_schema(request=UserAddressSerializer, tags=["Customer Profile"])
@api_view(['POST'])
def save_address(request):
    serializer = UserAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return success_response(
            message="تم إضافة العنوان بنجاح",
            data=serializer.data,
            status_code=201
        )
    return error_response(
        message="خطأ في البيانات المرسلة",
        errors=serializer.errors,
        status_code=400
    )


@extend_schema(tags=["Customer Profile"], responses=UserAddressSerializer(many=True))
@api_view(['GET'])
def list_addresses(request):
    addresses = UserAddress.objects.filter(user=request.user).order_by("-created_at")
    serializer = UserAddressSerializer(addresses, many=True)
    return success_response(
        message="تم جلب العناوين بنجاح",
        data=serializer.data
    )


@extend_schema(tags=["Customer Profile"])
@api_view(['DELETE'])
def delete_address(request, pk):
    try:
        address = UserAddress.objects.get(pk=pk, user=request.user)
    except UserAddress.DoesNotExist:
        return error_response(
            message="العنوان غير موجود",
            status_code=404
        )

    address.delete()
    return success_response(
        message="تم حذف العنوان بنجاح",
        status_code=200
    )