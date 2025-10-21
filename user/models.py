import datetime
import uuid
from io import BytesIO

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, User, AbstractUser, Permission, Group, \
    PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.validators import validate_integer
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image
from rest_framework_simplejwt.tokens import RefreshToken

from core.models.localization import Language
from helper.modelHelper import Active_Status, User_Position, Email_Validator, Access_Level, User_Status, Country_List, \
    Governorates_List, SAUDI_CITIES_BY_GOVERNORATE, Public_Status

from helper.viewHelper import get_file_path

from user.managers import TokenManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):

        if email is None:
            raise TypeError(_('Users must have an email address.'))
        if User.objects.filter(email=self.normalize_email(email).lower()).exists():
            raise ValueError('This email has already been registered.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = 'Active'
        user.is_staff = 'Active'
        user.is_active = 'Active'
        user.is_author = 'Active'
        user.admin = 'Active'
        user.is_customer = 'Active'
        user.is_verified = 'Active'
        user.is_online = 'Active'
        user.access_notification = 'Active'
        user.access_level = 'SuperAdmin'
        user.subscribe = 'Active'
        user.save()
        groups = Group.objects.get_or_create(name='superuser')
        groups = Group.objects.get(name='superuser')
        groups.user_set.add(user)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Description:This is going to be the main User Model
    """
    email = models.EmailField(verbose_name='email address', max_length=50, validators=[Email_Validator], unique=True,
                              error_messages={
                                  'unique': "This email has already been registered."},blank=True, null=True)

    first_name = models.CharField(max_length=25, blank=True, null=True)
    middle_name = models.CharField(max_length=25,  blank=True, null=True)
    last_name = models.CharField(max_length=25,  blank=True, null=True)
    position = models.CharField(max_length=30,  blank=True, null=True,
                                default='Client')
    phone = models.CharField(max_length=20, validators=[validate_integer], unique=True,
     error_messages={  'unique': "This Phone has already been registered."})
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    auth_provider = models.CharField(
        max_length=50, blank=False,
        null=False,  default='email')
    is_superuser = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    admin =models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_staff = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_author = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_active = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_verified = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    access_level = models.CharField(max_length=20, choices=Access_Level, default='Customer')
    access_notification = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    groups = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    have_wallet = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    fcm_token = models.TextField(blank=True)
    firebase_uid = models.CharField(max_length=255, blank=True, null=True, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    otp_verified = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    otp_attempts = models.IntegerField(default=0)
    otp_attempts_expiry = models.DateTimeField(blank=True, null=True)
    otp_attempts_limit = models.IntegerField(default=5)
    otp_attempts_reset_time = models.DateTimeField(blank=True, null=True)
    otp_attempts_reset_interval = models.IntegerField(default=15)  # in minutes
    otp_attempts_reset = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    otp_attempts_reset_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    is_online = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    hide_email = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    # --- Image thumbnail helpers ---
    def _build_thumb_name(self, image_name: str, width: int, height: int) -> str:
        import os
        dir_name, base = os.path.split(image_name)
        name, ext = os.path.splitext(base)
        thumb_dir = os.path.join(dir_name, 'thumbs') if dir_name else 'thumbs'
        return os.path.join(thumb_dir, f"{name}_{width}x{height}{ext}")

    def _ensure_thumbnail(self, width: int = 120, height: int = 120) -> str | None:
        if not self.image or not getattr(self.image, 'name', None):
            return None
        thumb_name = self._build_thumb_name(self.image.name, width, height)
        try:
            if default_storage.exists(thumb_name):
                return thumb_name
            with default_storage.open(self.image.name, 'rb') as f:
                img = Image.open(f)
                img.load()
                if img.mode in ("RGBA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
                    img = background
                else:
                    img = img.convert("RGB")
                img.thumbnail((width, height), Image.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                buffer.seek(0)
                default_storage.save(thumb_name, ContentFile(buffer.read()))
                return thumb_name
        except Exception:
            return None

    def get_image_thumbnail_url(self, size: str = '120x120') -> str | None:
        try:
            width, height = [int(x) for x in size.lower().split('x')]
        except Exception:
            width, height = 120, 120
        thumb_name = self._ensure_thumbnail(width, height)
        if thumb_name and default_storage.exists(thumb_name):
            return default_storage.url(thumb_name)
        try:
            return self.image.url if self.image else None
        except Exception:
            return None

    @property
    def image_thumb_url(self) -> str | None:
        return self.get_image_thumbnail_url('120x120')

    def __str__(self):
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name} (Email: {self.email})'
        else:
            return self.email

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = str(get_random_string(5).upper()
                           + str(uuid.uuid4()).split('-')[1] + 'NUC'
                           + uuid.uuid4().hex[:6].upper())
            self.slug = slugify(self.email)
            self.auth_provider = 'email'
        super(User, self).save(*args, **kwargs)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def get_full_name(self):
        full_name = None
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_admin(self):
        # "Is the user an admin member?"
        return self.is_admin

        # In this method, check that the date of the last visit is not older than 15 minutes

    def user_online(self):
        if self.last_activity:
            return (timezone.now() - self.last_activity) < timezone.timedelta(minutes=15)
        return False

    # If the user visited the site no more than 15 minutes ago,
    def get_online_info(self):
        if self.user_online():
            # then we return information that he is online
            return _('Online')
        if self.last_activity:
            # otherwise we write a message about the last visit
            return _('Last visit {}').format(naturaltime(self.last_activity))
            # If you have only recently added information about a user visiting the site
            # then for some users there may not be any information about the visit, we will return information that the last visit is unknown
        return _('Unknown')


class UserProfile(models.Model):
    # --- RELATIONSHIP ---
    # Changed to OneToOneField for a strict one-to-one link.
    # Uses settings.AUTH_USER_MODEL to prevent circular import errors.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # --- PERSONAL & IDENTITY INFO ---
    # Simplified to use just the DateField. The p_year, p_month, p_day fields were redundant.
    dob = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    residence = models.CharField(max_length=50, null=True, blank=True)
    is_citizen = models.CharField(max_length=10, choices=Public_Status, default='No', null=True, blank=True)
    # This is the single source of truth for the user's ID number now.
    id_number = models.CharField(max_length=50, null=True, blank=True)

    # --- IDENTITY DOCUMENTS (Moved from JobProvider) ---
    # These fields verify the person, so they belong on the personal profile.
    id_image_front = models.ImageField(upload_to=get_file_path, blank=True, null=True,
                                       help_text="Front of National ID/Passport")
    id_image_back = models.ImageField(upload_to=get_file_path, blank=True, null=True,
                                      help_text="Back of National ID/Passport")
    residence_image = models.ImageField(upload_to=get_file_path, blank=True, null=True,
                                        help_text="Proof of residence document")
    gender = models.CharField(max_length=10, choices=[("M", "Male"), ("F", "Female")], null=True, blank=True)
    # --- LOYALTY POINTS ---
    current_points = models.PositiveIntegerField(default=0)
    lifetime_points = models.PositiveIntegerField(default=0)
    points_spent = models.PositiveIntegerField(default=0)

    # --- PREFERENCES & SETTINGS ---
    country = models.TextField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    lang = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    dark_mode = models.CharField(max_length=10, choices=Active_Status, default='Inactive', null=True, blank=True)
    notification = models.CharField(max_length=10, choices=Active_Status, default='Active', null=True, blank=True)
    deactivate = models.CharField(max_length=10, choices=Active_Status, default='Inactive', null=True, blank=True)
    delete_account = models.CharField(max_length=10, choices=Active_Status, default='Inactive', null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user and (self.user.first_name or self.user.last_name):
            return f"{self.user.first_name} {self.user.last_name}"
        return f"UserProfile #{self.pk}"

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)




class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    label = models.CharField(max_length=100, validators=[UnicodeUsernameValidator], null=True, blank=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=SAUDI_CITIES_BY_GOVERNORATE, default='Cairo', null=True,
                                    blank=True)
    city = models.CharField(max_length=100,  null=True, blank=True)
    area = models.CharField(max_length=100,  null=True, blank=True)
    address = models.CharField(max_length=200, validators=[UnicodeUsernameValidator], null=True, blank=True)
    postal_code = models.CharField(max_length=100, validators=[validate_integer], null=True, blank=True)
    apartment = models.CharField(max_length=100, null=True, blank=True)
    building_name = models.CharField(max_length=255, null=True, blank=True)
    floor = models.CharField(max_length=50, null=True, blank=True)
    apartment_number = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    property_type = models.CharField(
        max_length=20,
        choices=[
            ("apartment", "شقة"),
            ("villa", "فيلا"),
            ("office", "مكتب"),
            ("house", "منزل"),
        ],
        null=True, blank=True
    )
    phone = models.CharField(max_length=100, validators=[validate_integer], null=True, blank=True)
    note = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], blank=True, null=True)
    default = models.CharField(max_length=20, choices=Active_Status, default='Inactive', null=True, blank=True)
    code = models.CharField(max_length=100,  null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    slug = models.SlugField(unique=True,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'UserAddress-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)

        super(UserAddress, self).save(*args, **kwargs)


class UserGeoInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.CharField(max_length=30, null=True, blank=True)
    device_type = models.CharField(max_length=300, null=True, blank=True)
    browser_type = models.CharField(max_length=300, null=True, blank=True)
    browser_version = models.CharField(max_length=300, null=True, blank=True)
    os_type = models.CharField(max_length=300, null=True, blank=True)
    os_version = models.CharField(max_length=300, null=True, blank=True)
    location_country = models.CharField(max_length=300, null=True, blank=True)
    location_city = models.CharField(max_length=300, null=True, blank=True)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user"]
        verbose_name_plural = "User Geo Info"

    def __str__(self):
        return self.user


class UserToken(models.Model):
    objects = TokenManager()
    REGISTRATION_TOKEN = 'rt'
    REGISTRATION_DELETE_TOKEN = 'rd'
    PASSWORD_CHANGE_TOKEN = 'pc'
    EMAIL_CHANGE_TOKEN = 'ec'
    TOKEN_TYPES = (
        (REGISTRATION_TOKEN, _('Registration token')),
        (REGISTRATION_DELETE_TOKEN, _('Registration Delete UserToken')),
        (PASSWORD_CHANGE_TOKEN, _('Password Change UserToken')),
        (EMAIL_CHANGE_TOKEN, _('Change Email UserToken')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TOKEN_TYPES, max_length=3, default=REGISTRATION_TOKEN)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def __str__(self):
        return self.token



    @property
    def expires_at(self):
        return self.created_at.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=self.lifetime)


class OtpCode(models.Model):
    OTP_TYPE_CHOICES = [
        ('general', 'General'),
        ('signup', 'Signup'),
        ('reset', 'Reset'),
    ]

    phone = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(seconds=300)  # 5 minutes default
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    class Meta:
        ordering = ['-created_at']  # Latest first