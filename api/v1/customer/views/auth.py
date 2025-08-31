# api/views/auth.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from user.models import User
from api.v1.customer.serializers.auth_serializer import RegisterSerializer , ConfirmOTPSerializer , UserAddressSerializer ,LogoutSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


VALID_ACCESS_LEVELS = ['Client', 'Provider']
@extend_schema(request=RegisterSerializer,tags=["CustomerAuth"] , auth=[])
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def register(request):
    """
    Step 1: Register with phone number and access level (Client Or Provider + send OTP)
    """
    phone = request.data.get("phone")
    access_level = request.data.get("access_level")

    if not phone or not access_level:
        return Response({"error": "Phone and access_level are required"}, status=status.HTTP_400_BAD_REQUEST)

    if access_level not in VALID_ACCESS_LEVELS:
        return Response({"error": f"access_level must be one of {VALID_ACCESS_LEVELS}"}, status=status.HTTP_400_BAD_REQUEST)

    
    user, created = User.objects.get_or_create(phone=phone, defaults={"position": access_level})

   
    if user.otp_attempts_reset_time and timezone.now() > user.otp_attempts_reset_time:
        user.otp_attempts = 0

   
    if user.otp_attempts >= user.otp_attempts_limit:
        return Response({"error": "Too many OTP requests. Please wait and try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    otp = get_random_string(6, allowed_chars="0123456789")
    user.access_level = access_level
    user.is_active = "Inactive"
    user.otp = otp
    user.otp_expiry = timezone.now() + timedelta(minutes=5)
    user.otp_attempts += 1
    user.otp_attempts_reset_time = timezone.now() + timedelta(minutes=user.otp_attempts_reset_interval)
    user.save()

    # send_sms(phone, f"Your OTP is {otp}")

    return Response({
        "message": "OTP sent to phone. Please confirm your account.",
        "phone": phone,
        "access_level": access_level,
        "otp_demo": otp  
    }, status=status.HTTP_201_CREATED)

@extend_schema(request=ConfirmOTPSerializer, auth=[],tags=["CustomerAuth"])
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def verify_otp(request):
    """
    Step 2: Verify OTP and activate user
    """
    phone = request.data.get("phone")
    otp = request.data.get("otp")

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


    if not user.otp or user.otp_expiry < timezone.now():
        return Response({"error": "OTP expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)


    if str(user.otp) != str(otp):
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


    user.is_active = "Active"
    user.otp_verified = "Active"
    user.otp = None  
    user.otp_expiry = None
    user.otp_attempts = 0  
    user.save()

    return Response({
        "message": "User verified successfully",
        "tokens": user.tokens()
    }, status=status.HTTP_200_OK)

@extend_schema(
    request=LogoutSerializer,tags=["CustomerAuth"],
    responses={200: {'message': 'Logged out successfully'}, 400: {'error': 'Invalid or expired token'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    serializer = LogoutSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        refresh_token = serializer.validated_data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"}, status=200)
    except Exception:
        return Response({"error": "Invalid or expired token"}, status=400)
