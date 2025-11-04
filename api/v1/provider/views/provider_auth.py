import random
import json
import random
from datetime import timedelta
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import *
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from api.v1.response import success_response, error_response
from api.v1.provider.serializers.auth import ProviderProfileCompletionSerializer, ProviderProfileDetailSerializer

from apps.classified.models.models import JobProvider
from user.models import OtpCode

User = get_user_model()



# Note: If get_default_sender raises ValueError, the server won't start until a sender is activated in the 4jawaly account.

# Existing send_sms_otp updated to use DEFAULT_SENDER_NAME


@csrf_exempt
def ProviderRegister(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone')

            if not all([email, password, first_name, last_name, phone]):  # Added phone as required for SMS
                return JsonResponse({'message': 'All fields including phone are required'},
                                    status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.create_user(email=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone
                user.is_active = False  # Set to inactive until SMS verification
                user.access_level = 'Customer'
                user.save()

            except ValueError as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({'message': f'Error creating user: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Send SMS OTP for signup verification
            otp = random.randint(100000, 999999)
            OtpCode.objects.create(
                phone=phone,
                otp=str(otp),
                type='signup',
                expires_at=timezone.now() + timedelta(seconds=300)
            )

            message = f"Your signup verification code is: {otp}"
            result = sms_gateway.send_sms(message=message, numbers=phone, sender=DEFAULT_SENDER_NAME or 'MANFZ')

            if not result.get("success"):
                return JsonResponse({'message': 'Failed to send verification SMS.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return JsonResponse({
                'message': 'Registration successful. Verify your phone with the OTP sent.',
                'user': {'id': user.id, 'email': user.email}
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'message': f'An unexpected error occurred: {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# New view to verify OTP for signup
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_signup_otp(request):
    phone_number = request.data.get('phone')
    otp_code = request.data.get('otp')

    if not phone_number or not otp_code:
        return Response({'error': 'Phone number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_objs = OtpCode.objects.filter(phone=phone_number, otp=otp_code, type='signup')
    if not otp_objs.exists():
        return Response({'error': 'Invalid OTP or phone number.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = otp_objs.first()
    if otp_obj.is_valid():
        otp_obj.delete()

        # Activate the user
        user = User.objects.filter(phone=phone_number).first()
        if user:
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response({
                'message': 'Phone verified and account activated successfully.',
                'token': token
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'OTP has expired or was not sent. Please register again.'},
                        status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetSMS(generics.GenericAPIView):


    def post(self, request):
        phone = request.data.get('phone', '')

        if User.objects.filter(phone=phone).exists():
            user = User.objects.get(phone=phone)
            otp = random.randint(100000, 999999)

            OtpCode.objects.create(
                phone=phone,
                otp=str(otp),
                type='reset',
                expires_at=timezone.now() + timedelta(seconds=300)
            )

            message = f"Your password reset code is: {otp}"
            result = sms_gateway.send_sms(message=message, numbers=phone, sender=DEFAULT_SENDER_NAME or 'MANFZ')

            if result.get("success"):
                return Response({'success': 'An OTP has been sent to your phone for password reset.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to send SMS.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': 'No user found with this phone number.'}, status=status.HTTP_400_BAD_REQUEST)


# New view to verify OTP for password reset
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_otp(request):
    phone_number = request.data.get('phone')
    otp_code = request.data.get('otp')

    if not phone_number or not otp_code:
        return Response({'error': 'Phone number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_objs = OtpCode.objects.filter(phone=phone_number, otp=otp_code, type='reset')
    if not otp_objs.exists():
        return Response({'error': 'Invalid OTP or phone number.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = otp_objs.first()
    if otp_obj.is_valid():
        otp_obj.delete()

        # Generate a reset token (similar to email reset)
        uidb64 = urlsafe_base64_encode(smart_bytes(User.objects.get(phone=phone_number).id))
        token = PasswordResetTokenGenerator().make_token(User.objects.get(phone=phone_number))

        return Response({
            'message': 'OTP verified. Proceed to reset password.',
            'uidb64': uidb64,
            'token': token
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'OTP has expired or was not sent. Please request a new one.'},
                        status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
@permission_classes([AllowAny])
def UserLogin(request):
    """
    Handles user login using email and password.
    On success, it returns JWT access and refresh tokens and saves the FCM token.
    """
    email = request.data.get('email')
    password = request.data.get('password')



    if not email or not password:
        return Response({
            'status': False,
            'message': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)

    if user is not None:
        # ▼▼▼ START OF CORRECTED LOGIC ▼▼▼

        # 1. Get the optional fcm_token from the request.
        fcm_token = request.data.get('fcm_token')

        # 2. If an fcm_token was sent by the client, always update it.
        # This ensures the user's latest device gets notifications.
        if fcm_token:
            user.fcm_token = fcm_token
            # Use update_fields for an efficient database query.
            user.save(update_fields=['fcm_token'])

        # ▲▲▲ END OF CORRECTED LOGIC ▲▲▲

        refresh = RefreshToken.for_user(user)
        total_posts = user.classified_ads.count() # Make sure this relation exists

        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'access_level': user.access_level,
            'slug': user.slug,
            'profile': user.image.url if user.image else None,
            'mobile': user.phone,
            'customer_total_post': total_posts
        }

        response_data = {
            'status': True,
            'message': 'User logged in successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # This is the block that returns 401 for bad credentials
        return Response({
            'status': False,
            'message': 'Invalid credentials, try again'
        }, status=status.HTTP_401_UNAUTHORIZED)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserLogout(request):
    """
    Logs out a user by blacklisting their refresh token.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def UserDeleteAccount(request):
    print('user', request.body, request.GET,'method', request.method)
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        token = body['token']
        user_token = Token.objects.get(key=token)
        user = User.objects.get(id=user_token.user_id)
        user.delete()
        return JsonResponse({'status': True, 'message': 'User Account Deleted successfully'}, status=HTTP_200_OK,safe=False)
    else:
        return JsonResponse({'status': False, 'message': 'Invalid credentials, try again', 'status_code': 1},
                            status=HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserChangePassword(request):
    """
    Handles a password change request for an authenticated user.
    """
    # The authenticated user is available via `request.user` thanks to IsAuthenticated
    user = request.user

    # Get passwords from the request data
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    # Check if the provided current password is correct
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is not correct.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update the password
    user.set_password(new_password)
    user.save()

    return Response(
        {'message': 'Password changed successfully'},
        status=status.HTTP_200_OK
    )



@extend_schema(
    tags=["Provider Profile"],
    request=ProviderProfileCompletionSerializer,
    responses={200: ProviderProfileDetailSerializer, 400: 'Error Response'}
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def completeProviderProfile(request):
    """
    API endpoint to save all provider details in a single update request.
    This is intended to be called once after a user's initial phone verification.
    """
    user = request.user
    
    # Check if the provider profile exists. If not, it's a 404 error.
    try:
        provider_profile = JobProvider.objects.get(user=user)
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى إتمام التسجيل أولاً.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProviderProfileCompletionSerializer(
        provider_profile, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )

    if serializer.is_valid():
        try:
            # The serializer's create method will now be used for the one-time completion
            # of the profile.
            provider_profile = serializer.save()
            return success_response(
                message="تم إكمال ملف مقدم الخدمة بنجاح",
                data=ProviderProfileDetailSerializer(provider_profile,context={'request': request}).data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(
                message="حدث خطأ أثناء إكمال الملف",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'detail': str(e)}
            )
    else:
        return error_response(
            message="فشل إكمال ملف مقدم الخدمة",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )
#============================================= last edits  ============================================= 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def ApiUserProfile(request):
    try:
        user = request.user
        address_instance = UserAddress.objects.filter(user=user).first()

        # ... (job_requests aggregation logic remains the same) ...
        job_requests = JobRequest.objects.filter(user=user).aggregate(
            pending_order=Count('id', filter=Q(progress='Pending')),
            active_order=Count('id', filter=Q(progress='In Progress')),
            complete_order=Count('id', filter=Q(progress='Completed')),
            total_order=Count('id')
        )

        # =================== THE FIX IS HERE ===================
        user_details = {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'phone': user.phone,
            'slug': user.slug,
            'address': address_instance.address if address_instance else None,
            'image': request.build_absolute_uri(user.image.url) if user.image else None,
            'access_level': user.access_level,

            # 'area' in the JSON should map to the Governorate from your database
            'area': {
                'id': address_instance.governorates,
                'service_area': address_instance.governorates
            } if address_instance and address_instance.governorates else None,

            # 'city' in the JSON should map to the City from your database
            'city': {
                'id': address_instance.city,
                'service_city': address_instance.city
            } if address_instance and address_instance.city else None,
        }
        # ========================================================

        profile_data = {
            'user_details': user_details,
            'pending_order': job_requests['pending_order'],
            'active_order': job_requests['active_order'],
            'complete_order': job_requests['complete_order'],
            'total_order': job_requests['total_order']
        }

        # FIX: Wrap the profile_data in a 'data' key to match what Flutter expects.
        final_response = {
            'status': True,
            'message': 'User profile retrieved successfully',
            'data': profile_data
        }

        return Response(final_response, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': False,
            'message': f'Error retrieving profile: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserProfileUpdate(request):
    """
        Updates the profile for the authenticated user.
        """
    user = request.user
    data = request.data

    # Update User model
    # The flutter app sends a single 'name', so we'll put it in 'first_name'
    user.first_name = data.get('name', user.first_name)
    user.phone = data.get('phone', user.phone)
    if 'image' in request.FILES:
        user.image = request.FILES['image']
    user.save()

    # Update or Create UserAddress model
    # This assumes one primary address per user.
    UserAddress.objects.update_or_create(
        user=user,
        defaults={
            'governorates': data.get('governorate'),
            'city': data.get('city'),
            'address': data.get('address'),
            'country': 'Saudi Arabia'  # Set default country
        }
    )

    # You should return the updated profile data, using a serializer is best practice
    # For now, a simple success message will work.
    return Response({'detail': 'Profile updated successfully'}, status=status.HTTP_200_OK)


def ApiUserOtp(request):
    if request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        otp = get_random_string(6, allowed_chars='1234567890')
        data = {'phone': phone, 'otp': otp}
        return JsonResponse(data, safe=False)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiUserDeviceToken(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        fcm_token = body['fcm_token']
        token = body['token']
        user_token = Token.objects.get(key=token)
        user = User.objects.get(id=user_token.user_id)
        if user.fcm_token == fcm_token:
            return JsonResponse({'status': 'already_registered', 'message': 'Token already saved'}, status=200)
        user.fcm_token = fcm_token
        user.save()
        return JsonResponse({'status': True, 'message': 'Device token saved successfully'}, status=200)
    return JsonResponse({'status': False, 'message': 'Not Post Request'}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    fcm_token = request.data.get('fcm_token')
    if not fcm_token:
        return Response({"error": "FCM token not provided"}, status=400)

    user = request.user
    user.fcm_token = fcm_token
    user.save(update_fields=['fcm_token'])
    return Response({"success": "FCM token updated"}, status=200)


@csrf_exempt
def ApiUserAddress(request,token):
    print('ApiUserAddress', request.body, 'method', request.method,'get',request.GET,'post',request.POST)
    print('token',token)
    if request.method == 'GET':
        # body_unicode = request.body.decode('utf-8')
        # body = json.loads(body_unicode)
        # token = body['token']
        # print('token', token)
        user_token = Token.objects.get(key=token)
        user = User.objects.get(id=user_token.user_id)
        address = UserAddress.objects.filter(user=user)
        serializer = UserAddressSerializer(address, many=True)
        success = True
        message = f"Success "
        address_data = serializer.data
        # serializers = {'category': category_serializer.data, 'products': product_serializer.data}
        data = {'success': success, 'data': address_data, 'message': message, }
        return JsonResponse(data, safe=False)
    else:
        success = False
        message = f"Error "
        address_data = {'data': [], }
        data = {'success': success, 'data': address_data, 'message': message, }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserAccountDelete(request):
    """
    Deactivates the authenticated user's account after verifying their password.
    """
    user = request.user

    # Retrieve data from query parameters to match the Flutter code
    password = request.query_params.get('password')
    reason = request.query_params.get('reason')
    description = request.query_params.get('description')

    # --- Security Check: Verify user's password ---
    if not password or not user.check_password(password):
        return Response(
            {'message': 'Incorrect password provided.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # --- Deactivation Logic ---
    # Instead of deleting, it's best practice to deactivate the user
    user.is_active = False
    user.save()

    # Optional: Log the deactivation reason
    print(f"User {user.email} deactivated. Reason: {reason}, Description: {description}")

    # Optional but recommended: Delete the user's auth token so it can't be reused
    if hasattr(request, 'auth') and request.auth:
        request.auth.delete()

    return Response(
        {'message': 'Your account has been successfully deleted.'},
        status=status.HTTP_200_OK
    )


@csrf_exempt
def ApiUserAddressSave(request):
    print('ApiUserAddressSave', request.body, 'method', request.method,'get',request.GET,'post',request.POST)
    try:

        if request.method == 'POST':
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            label = body['label']
            country = body['country']
            governorate = body['governorate']
            city = body['city']
            address = body['address']
            latitude = body['latitude']
            longitude = body['longitude']
            apartment = body['apartment']
            token = body['token']
            user_token = Token.objects.get(key=token)
            user = User.objects.get(id=user_token.user_id)
            print('user', user)
            governorate =governorate.replace('Governorate','')
            governorate = governorate.replace(' ','')
            city = city.replace('City','')

            try:
                address = UserAddress.objects.get(user=user, latitude=latitude,
                                  longitude=longitude)
                address.label = label
                address.address = address
                address.apartment = apartment
                address.save()
            except Exception as e:
                print('error user', e)

                address = UserAddress(user=user, label=label, country=country, governorates=governorate, city=city,
                                      address=address, apartment=apartment, latitude=latitude,
                                      longitude=longitude)
                address.save()
            address_serializer = UserAddressSerializer(address, many=False, context={'request': request})
            success = True
            message = f"Success "
            address_data = {'address': address_serializer.data,  }
            data = {'success': success, 'data': address_data,'slug':address.slug, 'message': message, }
            return JsonResponse(data, status=HTTP_201_CREATED, safe=False)
    except Exception as e:
        print('error user2', e)
        success = False
        message = f"Error {e} "
        address_data = {'address': [],'slug':'' }
        data = {'success': success, 'data': address_data, 'message': message, }
        return JsonResponse(data, status=HTTP_422_UNPROCESSABLE_ENTITY, safe=False)


@csrf_exempt
def ApiUserAddressUpdate(request,id):
    print('ApiUserAddressUpdate', request.body, 'method', request.method,'get',request.GET,'post',request.POST)
    try:

        if request.method == 'PUT':
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            token = body['token']
            label = body['label']
            country = body['country']
            governorate = body['governorate']
            city = body['city']
            address = body['address']
            apartment = body['apartment']
            latitude = body['latitude']
            longitude = body['longitude']
            user_token = Token.objects.get(key=token)
            user = User.objects.get(id=user_token.user_id)
            governorate =governorate.replace('Governorate','')
            governorate = governorate.replace(' ','')
            city = city.replace('City','')

            print('user', user)

            address_object = UserAddress.objects.get(id=id)
            address_object.label = label
            address_object.country = country
            address_object.governorates = governorate
            address_object.city = city
            address_object.address = address
            address_object.apartment = apartment
            address_object.latitude = latitude
            address_object.longitude = longitude
            address_object.save()

            address_serializer = UserAddressSerializer(address_object, many=False, context={'request': request})
            success = True
            message = f"Success "
            product_data = {'address': address_serializer.data,  }
            data = {'success': success, 'data': product_data, 'message': message, }
            return JsonResponse(data, status=HTTP_200_OK, safe=False)
    except Exception as e:
        print('error user2', e)
        success = False
        message = f"Error {e} "
        product_data = {'data': [], }
        data = {'success': success, 'data': product_data, 'message': message, }
        return JsonResponse(data, status=HTTP_422_UNPROCESSABLE_ENTITY, safe=False)
    success = False
    message = f"Some Thing Went Wrong"
    product_data = {'data': [], }
    data = {'success': success, 'data': product_data, 'message': message, }
    return JsonResponse(data, status=HTTP_400_BAD_REQUEST, safe=False)


@csrf_exempt
def ApiUserAddressDelete(request,id):
    try:

        if request.method == 'DELETE':
            address = UserAddress.objects.get(id=id)
            user_address = User.objects.get(id=address.user_id)
            address.delete()

            address = UserAddress.objects.filter(user=user_address)
            address_serializer = UserAddressSerializer(address, many=False, context={'request': request})
            success = True
            message = f"Success "
            product_data = {'address': address_serializer.data,  }
            data = {'success': success, 'data': product_data, 'message': message, }
            return JsonResponse(data, status=HTTP_202_ACCEPTED, safe=False)
    except Exception as e:
        print('error user2', e)
        success = False
        message = f"Error {e} "
        product_data = {'data': [], }
        data = {'success': success, 'data': product_data, 'message': message, }
        return JsonResponse(data, status=HTTP_422_UNPROCESSABLE_ENTITY, safe=False)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_by_phone(request):
    phone = request.data.get('phone')
    password = request.data.get('password')

    if not phone or not password:
        return Response({'error': 'Phone and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(phone=phone)
        user.set_password(password)
        user.save()
        return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print('e', e)
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
