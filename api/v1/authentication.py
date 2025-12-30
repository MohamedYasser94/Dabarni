# api/views/auth.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from user.models import User
from api.v1.global_serializer.auth_serializer import RegisterSerializer , ConfirmOTPSerializer ,LogoutSerializer, UpdateFCMTokenSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken ,TokenError
from rest_framework.permissions import IsAuthenticated
from api.v1.response import success_response, error_response
from apps.classified.models.models import JobProvider
from firebase_admin import auth as firebase_auth
import logging

logger = logging.getLogger(__name__)
VALID_ACCESS_LEVELS = ['Client', 'Provider']

@extend_schema(request=RegisterSerializer, tags=["Auth"], auth=[])
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
        return error_response(
            message="Phone and access_level are required",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if access_level not in VALID_ACCESS_LEVELS:
        return error_response(
            message=f"access_level must be one of {VALID_ACCESS_LEVELS}",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    created = False
    try:
        user = User.objects.get(phone=phone)
        
        if user.access_level != access_level:
            return error_response(
                message="This phone is already registered with a different role. Please use another phone number.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    except User.DoesNotExist:
        try:
            user = User.objects.create(phone=phone, access_level=access_level, position=access_level)
            created = True
        except Exception as e:
            return error_response(
                message=f"An error occurred while creating the user: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    if created and access_level == 'Provider':
        try:
            JobProvider.objects.create(
                user=user,
                business_phone=phone
                # Category is not set here, as it's now nullable
            )
        except Exception as e:
            user.delete()
            return error_response(
                message=f"An error occurred while creating provider profile: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    if user.otp_attempts_reset_time and timezone.now() > user.otp_attempts_reset_time:
        user.otp_attempts = 0

    if user.otp_attempts >= user.otp_attempts_limit:
        return error_response(
            message="Too many OTP requests. Please wait and try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

    otp = get_random_string(6, allowed_chars="0123456789")
    user.otp = otp
    user.otp_expiry = timezone.now() + timedelta(minutes=5)
    user.otp_attempts += 1
    user.otp_attempts_reset_time = timezone.now() + timedelta(minutes=user.otp_attempts_reset_interval)
    user.save()

    return success_response(
        message="OTP sent to phone. Please confirm your account.",
        data={
            "phone": phone,
            "access_level": access_level,
            "otp_demo": otp
        },
        status_code=status.HTTP_200_OK
    )

@extend_schema(request=ConfirmOTPSerializer, tags=["Auth"], auth=[])
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def verify_otp(request):
    """
    Step 2: Verify OTP, activate user, and generate Firebase Token
    """
    phone = request.data.get("phone")
    otp = request.data.get("otp")
    access_level = request.data.get("access_level")  

    if not phone or not otp or not access_level:
        return error_response(
            message="phone, otp and access_level are required",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(phone=phone, access_level=access_level)
    except User.DoesNotExist:
        return error_response(
            message="User not found with this phone and role",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    if not user.otp or user.otp_expiry < timezone.now():
        return error_response(
            message="OTP expired. Please request a new one",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if str(user.otp) != str(otp):
        return error_response(
            message="Invalid OTP",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    is_new_user = (
        user.otp_verified != "Active" or 
        not user.first_name or 
        not user.last_name
    )

    user.is_active = "Active"
    user.otp_verified = "Active"
    user.otp = None
    user.otp_expiry = None
    user.otp_attempts = 0
    user.save()
    firebase_token = None
    
    try:
        if not user.firebase_uid:
            # Ensure phone number is in E.164 format (e.g., +201060074850)
            formatted_phone = user.phone if user.phone.startswith('+') else f'+{user.phone}'

            try:
                # Try to get existing Firebase user by phone number
                existing_firebase_user = firebase_auth.get_user_by_phone_number(formatted_phone)
                user.firebase_uid = existing_firebase_user.uid
                user.save()
                logger.info(f"Linked existing Firebase user for {formatted_phone}")

            except firebase_auth.UserNotFoundError:
                # Create new Firebase user if not found
                try:
                    firebase_user = firebase_auth.create_user(
                        phone_number=formatted_phone,
                        display_name=f"{user.first_name} {user.last_name}" if user.first_name else "New User"
                    )
                    user.firebase_uid = firebase_user.uid
                    user.save()
                    logger.info(f"Created new Firebase user for {formatted_phone}")
                except firebase_auth.PhoneNumberAlreadyExistsError:
                    logger.warning(f"Phone number {formatted_phone} already exists in Firebase")
                    # Try to get the user again
                    existing_firebase_user = firebase_auth.get_user_by_phone_number(formatted_phone)
                    user.firebase_uid = existing_firebase_user.uid
                    user.save()
                except Exception as create_error:
                    error_msg = str(create_error)
                    logger.error(f"Error creating Firebase user: {error_msg}")

                    # Check if it's a configuration error
                    if "CONFIGURATION_NOT_FOUND" in error_msg or "auth provider" in error_msg.lower():
                        logger.error(
                            "Firebase Phone Authentication is not enabled. "
                            "Please enable it in Firebase Console: "
                            "Authentication > Sign-in method > Phone"
                        )
            except Exception as lookup_error:
                error_msg = str(lookup_error)
                logger.error(f"Error looking up Firebase user: {error_msg}")

                if "CONFIGURATION_NOT_FOUND" in error_msg or "auth provider" in error_msg.lower():
                    logger.error(
                        "Firebase Phone Authentication is not enabled. "
                        "Please enable it in Firebase Console: "
                        "Authentication > Sign-in method > Phone"
                    )

        if user.firebase_uid:
            additional_claims = {
                'django_user_id': user.id,
                'access_level': user.access_level,
                'phone': user.phone
            }
            custom_token_bytes = firebase_auth.create_custom_token(user.firebase_uid, additional_claims)
            firebase_token = custom_token_bytes.decode('utf-8')

    except Exception as e:
        logger.error(f"General Error generating Firebase token for user {user.phone}: {str(e)}")
    return success_response(
        message="User verified successfully",
        data={
            "message": "User verified successfully",
            "tokens": user.tokens(),
            "firebase_token": firebase_token,
            "firebase_uid": user.firebase_uid,
            "is_new_user": is_new_user,
            "user_status": "new" if is_new_user else "existing",
        },
        status_code=status.HTTP_200_OK
    )


@extend_schema(
    request=LogoutSerializer,
    tags=["Auth"],
    responses={
        200: {'message': 'Logged out successfully'},
        400: {'error': 'Invalid or expired token'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    serializer = LogoutSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    refresh_token = serializer.validated_data['refresh']
    try:
        token = RefreshToken(refresh_token)
        token.blacklist() 
        return success_response(
            message="Logged out successfully",
            status_code=status.HTTP_200_OK
            )
    except TokenError:
        return error_response(
            message="Invalid or expired token",
            status_code=status.HTTP_400_BAD_REQUEST
        )

