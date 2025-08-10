import json
import os

import jwt
from django.conf import settings
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Q
from django.http import HttpResponsePermanentRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status, views, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import *

from api.v1.renderers import UserRenderer
from api.v1.serializers.user import *
from api.v1.utils import *
from apps.classified.models.job import JobRequest
from core.models.subscriptions import *
from core.utils.backends import RandomPasswordGenerator
from user.models import UserAddress
import firebase_admin
from firebase_admin import auth as firebase_auth # Use an alias to avoid confusion
User = get_user_model()


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):

        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        status_code = status.HTTP_201_CREATED
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        # token = RefreshToken.for_user(user).access_token
        ###########  SEND TO VERIFY EMAIL  #################
        # current_site = get_current_site(request).domain
        # relativeLink = reverse('api:email-verify')
        # absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)
        # # email data
        # email_body = 'Hi ' + user.email + \
        #              ' Use the link below to verify your email \n' + absurl
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': 'Verify your email'}
        # Util.send_email(data)
        ############################################3
        return Response(user_data,
                        status=status.HTTP_201_CREATED)  # response = {  #     'success': 'True',  #     'status code': status_code,  #     'message': 'User registered  successfully',  #     'token': token,  # }  # return Response(response, status=status_code)  # return Response(user_data, status=status.HTTP_201_CREATED)


@csrf_exempt
def UserRegister(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone')

            if not all([email, password, first_name, last_name, phone]):
                return JsonResponse({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

            # --- Step 1: Create the user in Firebase Authentication ---
            try:
                # Use the aliased import 'firebase_auth'
                firebase_user = firebase_auth.create_user(
                    email=email,
                    password=password,
                    display_name=f"{first_name} {last_name}",
                    phone_number=phone
                )
                print(f"Successfully created new user in Firebase: {firebase_user.uid}")
            except Exception as e:
                print(f"Error creating user in Firebase: {e}")
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # --- Step 2: Create the user in the Django database ---
            # FIX: Call create_user on the User model's manager (User.objects)
            if not User.objects.filter(email=email).exists():
                user = User(
                    email=email,

                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    is_active='Active',  # Keep user inactive until they verify their email
                    access_level ='Customer'
                )
                user.set_password(password)  # Use set_password to hash the password
                user.save()
            else:
                return JsonResponse({'message': 'User with this email already exists in Django'},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Create a token for the new user
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return JsonResponse({
                'message': 'Registration successful. Please check your email to verify your account.',
                'token': token,
                'user': {'id': user.id, 'email': user.email}
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse({'message': f'An unexpected error occurred: {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# --- دالة SendOtpInMail لم تعد ضرورية ---
# يمكنك حذفها أو تركها فارغة
@csrf_exempt
def SendOtpInMail(request):
    return JsonResponse({
        'status': False,
        'message': 'This endpoint is no longer used. Email verification is now handled by Firebase.',
        'status_code': 410
    }, status=status.HTTP_410_GONE)

@csrf_exempt
def SendOtpInMailSuccess(request):
    print('user', request.body, 'method', request.method)
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            user_id = body.get('user_id')
            email_verified = body.get('email_verified')

            if not user_id or email_verified is None:
                return JsonResponse({
                    'status': False,
                    'message': 'User ID and email_verified are required',
                    'status_code': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(id=user_id).first()
            if user:
                user.is_verified = bool(email_verified)  # Set is_verified based on email_verified
                user.save()
                return JsonResponse({
                    'status': True,
                    'message': 'Email verification status updated successfully',
                    'status_code': 200
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'status': False,
                    'message': 'User not found',
                    'status_code': 404
                }, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            print('Invalid JSON data:', request.body)
            return JsonResponse({
                'status': False,
                'message': 'Invalid JSON data',
                'status_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({
            'status': False,
            'message': 'Method not allowed',
            'status_code': 405
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AllowAny])
def UserLogin(request):
    """
    Handles user login using email and password.
    On success, it returns JWT access and refresh tokens.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({
            'status': False,
            'message': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(email=email, password=password)

    if user is not None:
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)

        # Prepare user data to send back to the app
        # Using a serializer is best practice, but a dictionary works too.
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'access_level': user.access_level,
            'slug': user.slug,
        }

        # The response now includes both access and refresh tokens
        response_data = {
            'status': True,
            'message': 'User logged in successfully',
            'access': str(refresh.access_token),  # The token for API requests
            'refresh': str(refresh),  # The token to get a new access token
            'user': user_data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # If authentication fails
        return Response({
            'status': False,
            'message': 'Invalid credentials, try again'
        }, status=status.HTTP_401_UNAUTHORIZED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description',
        type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


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


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + absurl + "?redirect_url=" + redirect_url
            data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'UserToken is not valid, please request a new one'},
                                status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
def ApiCheckUserDataExist(request, data):
    if request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    user = False
    user_exist = False
    if request.method == 'POST':
        type = request.POST.get('type')

        if type == 'email':
            user = User.objects.filter(email=data).count()
        elif type == 'phone':
            user = User.objects.filter(phone=data).count()
        if user > 0:
            user_exist = True
            return JsonResponse(user_exist, safe=False)
        elif user <= 0:
            user_exist = False
            return JsonResponse(user_exist, safe=False)


@csrf_exempt
def ApiPromoCodeClient(request, coupon):
    if request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print(coupon)

    coupon = SubscriptionCoupon.objects.filter(coupon=coupon, status='Active')
    serializer = CheckCouponExistSerializer(coupon, many=True)
    return JsonResponse(serializer.data, safe=False)


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

        user_details = {
            'id': user.id,
            'name': user.get_full_name(),
            'email': user.email,
            'phone': user.phone,
            'address': address_instance.address if address_instance else None,
            'image': request.build_absolute_uri(user.image.url) if user.image else None,
            'access_level': user.access_level,
            'city': {
                'id': address_instance.governorates,
                'service_city': address_instance.governorates
            } if address_instance and address_instance.governorates else None,
            'area': {
                'id': address_instance.city,
                'service_area': address_instance.city
            } if address_instance and address_instance.city else None,
        }

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

@api_view(['GET']) # Use DRF decorator
@permission_classes([IsAuthenticated]) # Use DRF permission to protect the view
@csrf_exempt # Keep if you need it, but it's often not needed with token auth
def UserModulePermission(request):
    """
    This view now correctly uses DRF's authentication system.
    """
    try:
        # Now you can safely use request.user, DRF has already verified it.
        user = request.user
        user_serializer = UserSerializer(user, many=False, context={'request': request})
        data = {'status': True, 'message': 'User Module Permission', 'data': user_serializer.data}
        # Use DRF's Response object
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'status': False, 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
