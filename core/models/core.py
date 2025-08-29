import os
from io import BytesIO
from pathlib import Path

import barcode
import pyqrcode
import qrcode
from PIL import Image, ImageDraw
from barcode.writer import ImageWriter
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.validators import EmailValidator, validate_integer
from django.db import models
from django.urls import reverse

from core.models.localization import *
from Dabarni.settings import MEDIA_ROOT
from helper.modelHelper import *
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()

class SiteSetting(models.Model):
    title = models.CharField(max_length=20,validators=[UnicodeUsernameValidator], null=True,blank=True, default='Digithup')
    keywords = models.CharField(max_length=255,validators=[UnicodeUsernameValidator], null=True,blank=True, default='Digithup')
    copyright = models.CharField(max_length=50,validators=[UnicodeUsernameValidator], null=True,blank=True, default='Digithup')
    email = models.EmailField(max_length=50,validators=[EmailValidator],  null=True,blank=True, default='info@Digithup.com')
    image = models.ImageField(upload_to=get_file_path,default='static/digithup/tetxtmix.png', null=True, blank=True)
    logo = models.ImageField(upload_to=get_file_path,default='static/digithup/tetxtmix.png', null=True, blank=True)
    dark_logo = models.ImageField(upload_to=get_file_path,default='static/digithup/tetxtmix.png', null=True, blank=True)
    favicon = models.ImageField(upload_to=get_file_path,default='static/digithup/tetxtmix.png', null=True, blank=True)
    map = models.TextField(validators=[UnicodeUsernameValidator], null=True, blank=True)
    domain = models.URLField(max_length=50, default='', null=True, blank=True)
    country = models.CharField(max_length=50, choices=Country_List, null=True, blank=True, default='Egypt')
    phone = models.CharField(max_length=50,validators=[validate_integer], null=True,blank=True, default='01000000000')
    address = models.CharField( max_length=100,validators=[UnicodeUsernameValidator], null=True,blank=True,default='Cairo')
    about = models.CharField(max_length=100,validators=[UnicodeUsernameValidator], blank=True, null=True,default='Digithup')
    type = models.CharField(max_length=20, choices=Site_Type, default='Backend', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Active_Status, default='Active', )
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'SiteSetting-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SiteSetting, self).save(*args, **kwargs)


class SystemSetting(models.Model):
    title = models.CharField(max_length=40, default='Digithup', null=True)
    app = models.CharField(max_length=40,choices=Current_App, default='Digithup', null=True)
    frontend_temp = models.CharField(max_length=40, default='creasoon', null=True,choices=FRONTEND_TEMPLATES,)
    home_index = models.CharField(max_length=40, default='content', null=True, choices=Home_Index, )
    backend_temp = models.CharField(max_length=40, default='good', null=True,blank=True,choices=BACKEND_TEMPLATES,)
    maintenance_temp = models.CharField(max_length=40, default='creasoon', null=True, blank=True, choices=MAINTENANCE_TEMPLATES, )
    vendor = models.CharField(max_length=20, choices=Active_Status, default='Inactive', )
    fb_id = models.CharField(max_length=150, default='', null=True,blank=True)
    fb_secret = models.CharField(max_length=150, default='', null=True,blank=True)
    gp_id = models.CharField(max_length=150, default='', null=True,blank=True)
    gb_secret = models.CharField(max_length=150, default='', null=True,blank=True)
    email_host = models.CharField(max_length=150, default='', null=True,blank=True)
    email_user = models.CharField(max_length=1500, default='', null=True,blank=True)
    email_pass = models.CharField(max_length=150, default='', null=True,blank=True)
    email_port = models.CharField(max_length=150, default='', null=True,blank=True)
    email_use_tls = models.CharField(max_length=150, default='', null=True,blank=True)
    email_from = models.CharField(max_length=150, default='', null=True,blank=True)

    api_url = models.CharField(max_length=150, default='', null=True,blank=True)
    maintenance = models.CharField(max_length=20, choices=Active_Status, default='Inactive', )
    membership = models.CharField(max_length=20, null=True, blank=True, choices=Active_Status, default='Inactive', )
    registration = models.CharField(max_length=30, null=True, blank=True, choices=Signin_Type, default='NotNeedActive', )
    status = models.CharField(max_length=20, choices=Active_Status, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'System-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SystemSetting, self).save(*args, **kwargs)


class ConfigSetting(models.Model):
    # Existing fields (renamed for clarity where needed)
    company_name = models.CharField(max_length=100, default='', null=True, blank=True)
    company_email = models.EmailField(max_length=100, default='', null=True, blank=True)
    phone = models.CharField(max_length=100, default='', null=True, blank=True)
    logo = models.ImageField(upload_to='get_file_path', null=True,
                             blank=True)  # Ensure get_file_path is correctly defined
    dark_logo = models.ImageField(upload_to='get_file_path', null=True, blank=True)
    icon = models.ImageField(upload_to='get_file_path', null=True, blank=True)

    # System settings from Flutter app
    maintenance_mode = models.CharField(max_length=1, default='0', help_text="Use '1' for true, '0' for false")
    currency_symbol = models.CharField(max_length=10, default='$', null=True, blank=True)
    currency_symbol_position = models.CharField(max_length=10, default='left', null=True, blank=True)

    # General Settings
    privacy_policy = models.TextField(default='', null=True, blank=True)
    terms_conditions = models.TextField(default='', null=True, blank=True)
    contact_us = models.TextField(default='', null=True, blank=True)
    default_language = models.CharField(max_length=50, default='en', null=True, blank=True)

    # App Update Settings
    force_update = models.CharField(max_length=1, default='0', help_text="Use '1' for true, '0' for false")
    android_version = models.CharField(max_length=20, default='1.0.0', null=True, blank=True)
    ios_version = models.CharField(max_length=20, default='1.0.0', null=True, blank=True)
    play_store_link = models.URLField(max_length=255, default='', null=True, blank=True)
    app_store_link = models.URLField(max_length=255, default='', null=True, blank=True)

    # Ad Settings
    banner_ad_status = models.CharField(max_length=1, default='0', help_text="Use '1' for true, '0' for false")
    banner_ad_android_ad = models.CharField(max_length=255, default='', null=True, blank=True)
    banner_ad_ios_ad = models.CharField(max_length=255, default='', null=True, blank=True)
    interstitial_ad_status = models.CharField(max_length=1, default='0', help_text="Use '1' for true, '0' for false")
    interstitial_ad_android_ad = models.CharField(max_length=255, default='', null=True, blank=True)
    interstitial_ad_ios_ad = models.CharField(max_length=255, default='', null=True, blank=True)
    native_ad_status = models.CharField(max_length=1, default='0', help_text="Use '1' for true, '0' for false")
    native_ad_android_ad = models.CharField(max_length=255, default='', null=True, blank=True)
    native_ad_ios_ad = models.CharField(max_length=255, default='', null=True, blank=True)

    # Authentication & Location
    default_latitude = models.CharField(max_length=50, default='26.160356', null=True, blank=True)
    default_longitude = models.CharField(max_length=50, default='32.726242', null=True, blank=True)
    mobile_authentication = models.CharField(max_length=1, default='1', help_text="Use '1' for true, '0' for false")
    google_authentication = models.CharField(max_length=1, default='1', help_text="Use '1' for true, '0' for false")
    apple_authentication = models.CharField(max_length=1, default='1', help_text="Use '1' for true, '0' for false")
    email_authentication = models.CharField(max_length=1, default='1', help_text="Use '1' for true, '0' for false")
    min_radius = models.CharField(max_length=10, default='0', null=True, blank=True)
    max_radius = models.CharField(max_length=10, default='500', null=True, blank=True)
    otp_service_provider = models.CharField(max_length=50, default='default', null=True, blank=True)
    map_provider = models.CharField(max_length=50, default='google', null=True, blank=True)

    # Other settings from enum
    demo_mode = models.CharField(max_length=1, default='0', help_text="Use '1' for true, '0' for false")
    auto_approve_edited_item = models.CharField(max_length=1, default='1', help_text="Use '1' for true, '0' for false")



    # Internal fields
    status = models.CharField(max_length=20, default='Active')  # choices=Active_Status
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name or "System Configuration"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Config-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ConfigSetting, self).save(*args, **kwargs)




class QrCode(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='qrocde_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='qrocde_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='qrocde_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=200, blank=True, null=True,default='QrCode')
    description = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True, default=626)
    width = models.IntegerField(blank=True, null=True, default=426)
    used = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    url = models.URLField()
    image = models.ImageField(upload_to='images/qrcode/%Y/%m', blank=True)
    qr_code = models.TextField(blank=True)
    qr_logo = models.ImageField(upload_to='images/qrcode/logo/%Y/%m', blank=True)
    icon = models.ImageField(upload_to='images/qrcode/icon/%Y/%m', blank=True)
    svg = models.ImageField(upload_to='images/qrcode/svg/%Y/%m', blank=True)
    barcode_class = models.CharField(max_length=500, choices=Barcode_Class, default='ean13', null=True, blank=True)
    barcode_number = models.CharField(max_length=250,blank=True, null=True,unique=True)
    barcode_image   = models.ImageField(upload_to='images/barcode/%Y/%m', blank=True)
    barcode_url = models.URLField(blank=True,null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('qrcode:qrcode_detail', args=[self.slug])

    def __str__(self):
        return self.name

    def generate_barcode(self,*args, **kwargs):
        EAN = barcode.get_barcode_class('code128')
        ean = EAN(f'{self.barcode_number}', writer=ImageWriter())
        self.barcode_number = ean.get_fullcode()
        self.barcode_class = EAN.name
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode_image.save(f'{self.barcode_number}.png', File(buffer),save=True)
        super(QrCode, self).save(*args, **kwargs)

    def generate_qr_code_svg(self):
        url = pyqrcode.create(self.url)
        try:
            check_path =Path(f'{MEDIA_ROOT}/qrcode/%y/%m/').exists()
            if check_path:
                pass
            else:
                os.makedirs(f'{MEDIA_ROOT}/qrcode/%y/%m/')
        except :
            os.makedirs(f'{MEDIA_ROOT}/qrcode/%y/%m/')
        svg = url.svg(f'{MEDIA_ROOT}/qrcode/%y/%m/{self.code}.svg', scale=8)
        self.svg.save(f'svg{self.name}-{self.barcode_number}.svg', File(open(f'{MEDIA_ROOT}/qrcode/%y/%m/{self.code}.svg', 'rb')), save=True)
        self.qr_code = url.terminal(quiet_zone=1)

    def get_qrcode_with_logo(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=7,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.convert("RGBA")

        img_w, img_h = img.size
        factor = 4

        buffer = BytesIO()
        img.save(buffer, "PNG")
        self.qr_logo.save(f'image{self.name}-{self.barcode_number}.png', File(buffer), save=False)

    def generate_qr_code_img(self, ):
        qrcode_img = qrcode.make(self.url)
        canvas = Image.new("RGB", (self.height, self.width), "white")
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        buffer = BytesIO()
        canvas.save(buffer, "PNG")
        self.image.save(f'image{self.name}-{self.barcode_number}', File(buffer), save=False)
        canvas.close()

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'QrCode-{get_random_string(5).upper()}'
            self.code = code

            self.slug = slugify(code)
            self.generate_qr_code_svg()
            self.generate_qr_code_img()
            self.get_qrcode_with_logo()
            self.generate_barcode()
        super(QrCode, self).save(*args, **kwargs)



    def get_absolute_url(self):
        return reverse('qrcode-detail', kwargs={'slug': self.slug})

    def get_downlaod_url(self):
        return self.qr_logo.url


class CommonMediaFiles(models.Model):
    owner_model = models.ForeignKey(ContentType,related_name='common_media', on_delete=models.CASCADE,null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=MultiFile_Type, null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    video_cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    file = models.FileField(upload_to=get_file_path, blank=True, null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'CommonMediaFiles-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonMediaFiles, self).save(*args, **kwargs)

class CommonTags(models.Model):
    owner_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.CharField(max_length=1500, null=False, blank=False)
    keyword = models.CharField(max_length=3500, null=False, blank=False)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Inactive')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home:FrontArticleTagDetails', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'Tag-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonTags, self).save(*args, **kwargs)

class CommonSeo(models.Model):
    owner_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    meta_title = models.CharField(max_length=500,validators=[UnicodeUsernameValidator],)
    meta_description = models.CharField(max_length=500,validators=[UnicodeUsernameValidator], verbose_name='Meta Tag description')
    meta_keywords = models.CharField(max_length=500,validators=[UnicodeUsernameValidator],)
    meta_author = models.ForeignKey(User, on_delete=models.CASCADE ,blank=True,null=True)
    seo_image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CommonSeo-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonSeo, self).save(*args, **kwargs)


class CommonComment(models.Model):
    owner_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    profile = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50,validators=[UnicodeUsernameValidator],)
    email = models.EmailField(validators=[Email_Validator],)
    body = models.TextField(verbose_name='Enter Comment')
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Commented {self.name} on {self.owner_id}.'

    class Meta:
        ordering = ('-update_at',)
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CommonComment-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonComment, self).save(*args, **kwargs)


class CommonSocialLink(models.Model):
    owner_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    provider = models.CharField(max_length=100, choices=Social_Providers, null=True, blank=True, default='facebook')
    url= models.CharField(max_length=250,  null=True, default='facebook')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CommonSocialLink-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonSocialLink, self).save(*args, **kwargs)








class CommonTranslate(models.Model):
    owner_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.TextField(blank=True,null=True)
    keyword = models.TextField(blank=True,null=True )
    body = models.TextField(blank=True,null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'CommonTranslate-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonTranslate, self).save(*args, **kwargs)



class HelpCategories(models.Model):
    title = models.CharField(max_length=100,choices=Help_Categories, blank=True, null=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'
        # verbose_name_plural = 'categories'

    class TranslatableMeta:
        fields = ['title', ]

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'HelpCat{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(HelpCategories, self).save(*args, **kwargs)


class HelpQuestions(models.Model):
    category = models.ForeignKey(HelpCategories, on_delete=models.CASCADE)
    title = models.TextField(validators=[UnicodeUsernameValidator], blank=True, null=True)
    keyword = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    views = models.IntegerField(default=0)
    popular = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'HelpQues{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(HelpQuestions, self).save(*args, **kwargs)


class CommonUrlShortener(models.Model):
    owner_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.TextField( validators=[UnicodeUsernameValidator],blank=True,null=True)
    keyword = models.TextField(blank=True,null=True )
    url =models.URLField(blank=True,null=True)
    short_url = models.URLField(blank=True,null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CommonUrlShortener-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CommonUrlShortener, self).save(*args, **kwargs)