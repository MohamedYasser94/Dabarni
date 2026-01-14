from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.utils import timezone
from api.v1.global_serializer.auth_serializer import EmailVerificationRequestSerializer, EmailVerifySerializer
from api.v1.utils import Util, handle_email_otp_sending
from user.models import User
from datetime import timedelta

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def request_email_verification(request):
    """
    Step 1: Update User Email (if changed) and Request Email Verification OTP.
    Body: {"email": "new_email@example.com"}
    """
    serializer = EmailVerificationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_email = serializer.validated_data['email']
    user = request.user

    if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
        return Response({
            'error': 'This email is already associated with another account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    success, otp_code = handle_email_otp_sending(user)

    if not success:
        return Response({'error': otp_code}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    email_body = (
        f'Hello {user.first_name or "User"},\n\n'
        f'Your Email Verification Code is: {otp_code}\n\n'
        f'This code is valid for 10 minutes.\n'
    )

    data = {
        'email_subject': 'Verify Your Email Address',
        'email_body': email_body,
        'to_email': new_email
    }

    try:
        Util.send_email(data)
        return Response({
            'success': True,
            'message': f'Email verification OTP sent to {new_email}'
        }, status=status.HTTP_200_OK)
        
    except Exception as exc:
        return Response({
            'error': 'Failed to send verification email.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def verify_email_otp(request):
    """
    Step 2: Verify the OTP and update the email.
    Body: {"email": "user@example.com", "otp": "123456"}
    """
    serializer = EmailVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_email = serializer.validated_data['email']
    otp_input = serializer.validated_data['otp']
    user = request.user

    if not user.email_verification_otp or user.email_verification_otp != otp_input:
        return Response({'error': 'Invalid OTP code.'}, status=status.HTTP_400_BAD_REQUEST)

    if user.email_verification_otp_created_at:
        expiration_time = user.email_verification_otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiration_time:
            return Response({'error': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

    if user.email != new_email:
        user.email = new_email
    
    user.is_verified = 'Active'
    user.email_verification_otp = None
    user.email_verification_otp_created_at = None
    user.save()

    return Response({
        'success': True,
        'message': 'Email verified successfully. You can now login.'
    }, status=status.HTTP_200_OK)