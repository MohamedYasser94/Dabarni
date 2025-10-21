from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from django.db import transaction
from apps.classified.models.models import JobCategories, JobProvider
from user.models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id',  'first_name','last_name','phone','email','image','access_level']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'email': 'The email should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone']

    def validate(self, attrs):
        if email := attrs.get('email', ''):
            return attrs
        else:
            raise serializers.ValidationError(self.default_error_messages)

    def create(self, validated_data):
        user_object = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],

        )
        user_object.set_password(validated_data['password'])
        user_object.save()
        return user_object


class LoginSerializer(serializers.Serializer):





    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    email = serializers.CharField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong email or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "email" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('UserToken is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')



class ProviderProfileCompletionSerializer(serializers.ModelSerializer):
    """
    Serializer to complete a provider's profile in a single request.
    It handles all fields from the registration form across multiple models.
    """
    full_name = serializers.CharField(required=True, write_only=True)
    
    # Fields for the UserProfile model
    is_citizen = serializers.BooleanField(required=True, write_only=True)
    id_image_front = serializers.ImageField(required=True, write_only=True)
    # id_image_back = serializers.ImageField(required=False, write_only=True)
    residence_image = serializers.ImageField(required=False, write_only=True)

    # JobProvider model fields
    category = serializers.SlugRelatedField(
        queryset=JobCategories.objects.all(),
        slug_field='slug',
        help_text="The slug of the job category."
    )
    address = serializers.CharField(required=True)
    user_image = serializers.ImageField(required=False, write_only=True)
    
    class Meta:
        model = JobProvider
        fields = [
            'full_name', 'is_citizen', 'id_image_front', 
            'residence_image', 'category',
            'address','user_image',
            # 'id_image_back',
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            user = self.context.get('request').user
            
            # Update User fields
            full_name = validated_data.pop('full_name').strip()
            name_parts = full_name.split()

            user.first_name = name_parts[0] if name_parts else ""
            user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            user.save()
            
            # Update or create the UserProfile instance
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.is_citizen = validated_data.pop('is_citizen')
            profile.id_image_front = validated_data.pop('id_image_front')
            # profile.id_image_back = validated_data.pop('id_image_back', None)
            profile.residence_image = validated_data.pop('residence_image', None)
            profile.save()
            
            # Update the existing JobProvider instance with all remaining data
            provider = JobProvider.objects.get(user=user)
            for attr, value in validated_data.items():
                setattr(provider, attr, value)
            provider.save()
        
        return provider
class ProviderProfileDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to display a full provider profile, including related user
    and user profile data.
    """
    # User model fields
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    # UserProfile model fields
    is_citizen = serializers.BooleanField(source='user.profile.is_citizen', read_only=True)
    id_image_front = serializers.ImageField(source='user.profile.id_image_front', read_only=True)
    id_image_back = serializers.ImageField(source='user.profile.id_image_back', read_only=True)
    residence_image = serializers.ImageField(source='user.profile.residence_image', read_only=True)
    user_image = serializers.ImageField(source='user.profile.user_image', read_only=True)

    # JobProvider model fields
    category_title = serializers.CharField(source='category.title', read_only=True)
    
    class Meta:
        model = JobProvider
        fields = [
            # From User
            'user_first_name', 'user_last_name', 'user_phone',
            
            # From UserProfile
            'is_citizen', 'user_image', 'id_image_front', 'id_image_back', 'residence_image',

            # From JobProvider
            'category_title', 'experience_years', 'company', 'bio',
            'address', 'latitude', 'longitude',
            'commercial_image', 'vat_image', 'license_image',
            'profile_completion_percentage',
        ]

class ProviderProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer to update a provider's full profile.
    It handles fields from User, UserProfile, and JobProvider models.
    """
    # Fields from the User model
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, write_only=True)
    
    # Fields from the UserProfile model (assumed to exist)
    dob = serializers.DateField(required=False)
    nationality = serializers.CharField(required=False)
    residence = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    is_citizen = serializers.BooleanField(required=False)
    id_image_front = serializers.ImageField(required=False)
    # id_image_back = serializers.ImageField(required=False)
    residence_image = serializers.ImageField(required=False)
    
    # Fields from the JobProvider model
    category = serializers.SlugRelatedField(
        queryset=JobCategories.objects.all(),
        slug_field='slug',
        required=False
    )
    experience_years = serializers.IntegerField(required=False)
    company = serializers.CharField(required=False)
    # bio = serializers.CharField(required=False)
    commercial_number = serializers.CharField(required=False)
    commercial_image = serializers.ImageField(required=False)
    # vat_image = serializers.ImageField(required=False)
    # license_image = serializers.ImageField(required=False)

    class Meta:
        model = JobProvider
        fields = [
            'first_name', 'last_name', 'email', 'dob', 'nationality',
            'residence', 'id_number', 'is_citizen', 'id_image_front',
            'residence_image', 'category', 'experience_years',
            'company', 'commercial_number', 'commercial_image',
            # 'bio', 'id_image_back', 'vat_image', 'license_image',
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            user = instance.user
            
            # Update User model fields
            user.first_name = validated_data.pop('first_name', user.first_name)
            user.last_name = validated_data.pop('last_name', user.last_name)
            user.email = validated_data.pop('email', user.email)
            user.save()
            
            # Update UserProfile model fields (assumed to exist)
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.dob = validated_data.pop('dob', profile.dob)
            profile.nationality = validated_data.pop('nationality', profile.nationality)
            profile.residence = validated_data.pop('residence', profile.residence)
            profile.id_number = validated_data.pop('id_number', profile.id_number)
            profile.is_citizen = validated_data.pop('is_citizen', profile.is_citizen)
            profile.id_image_front = validated_data.pop('id_image_front', profile.id_image_front)
            # profile.id_image_back = validated_data.pop('id_image_back', profile.id_image_back)
            profile.residence_image = validated_data.pop('residence_image', profile.residence_image)
            profile.save()

            # Update JobProvider model fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'
