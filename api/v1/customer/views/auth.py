# api/views/auth.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from user.models import User
from api.v1.customer.serializers.auth_serializer import RegisterSerializer , ConfirmOTPSerializer , UserAddressSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
VALID_ACCESS_LEVELS = ['Client', 'Provider']


@api_view(['POST'])
@extend_schema(request=RegisterSerializer,auth=[])
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
    
    if User.objects.filter(phone=phone).exists():
        return Response({"error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
    
    otp = get_random_string(6, allowed_chars="0123456789")

    user, created = User.objects.get_or_create(phone=phone,position=access_level,)
    user.access_level = access_level
    user.is_active = "Inactive"  
    user.otp = otp
    user.otp_expiry = timezone.now() + timedelta(minutes=5)
    user.save()

    
    # send_sms(phone, f"Please confirm your account. OTP: {otp}")

    return Response({
        "message": "OTP sent to phone. Please confirm your account.",
        "phone": phone,
        "access_level": access_level,
        "otp_demo": otp 
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@extend_schema(request=ConfirmOTPSerializer , auth=[] )
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
    print(user.otp)
    print(otp)
    print(user.otp_expiry , '<' , timezone.now())
    if user.otp != otp or user.otp_expiry < timezone.now():
        print("Time now ",timezone.now())
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = "Active"
    user.otp_verified = "Active"
    user.save()

    return Response({
        "message": "User verified successfully",
        "tokens": user.tokens()
    }, status=status.HTTP_200_OK)

@extend_schema(request=UserAddressSerializer)
@api_view(['POST'])
def save_address(request):
    """
    Create user address (manual or map selection)
    """
    serializer = UserAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @extend_schema(responses=UserAddressSerializer(many=True))
# @api_view(['GET'])
# def list_addresses(request):
#     """
#     Get all addresses for logged-in user
#     """
#     addresses = UserAddress.objects.filter(user=request.user)
#     serializer = UserAddressSerializer(addresses, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)