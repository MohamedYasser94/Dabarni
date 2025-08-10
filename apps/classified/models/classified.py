
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import JSONField
from django.urls import reverse
from django.utils.crypto import get_random_string
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from pilkit.processors import ResizeToFill
from slugify import slugify

from core.models.core import CommonMediaFiles, CommonTranslate
from core.models.localization import Currency, Governorates
from core.utils.backends import current_language
from helper.modelHelper import *
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()


class ClassifiedCategories(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=500,)
    keyword = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    color = models.CharField(max_length=20, blank=True, null=True,default='#000000',choices=COLORS)
    job_category = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    class TranslatableMeta:
        fields = ['title', ]

    def __str__(self):
        return self.title



    def get_absolute_url(self):
        return reverse("category_list")

    def get_front_url(self):
        return reverse('home:FrontClassifiedCategoryDetails', kwargs={'slug': self.slug})

    def get_image(self):
        try:
            return self.image.url
        except:
            return None

    def get_color(self):
        colors = dict(COLORS)
        for key, value in colors.items():
            if key == self.color:
                return value

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'ClassifiedCategories-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedCategories, self).save(*args, **kwargs)


class ClassifiedLocation(models.Model):
    country = models.CharField(max_length=100, blank=True, null=True, choices=Country_List, default='None')
    governorate = models.CharField(max_length=100, blank=True, null=True ,choices=Governorates_List,default='None')
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city}, {self.region}, {self.country}"


    def get_front_url(self):
        return reverse('home:FrontClassifiedPlacesDetails', kwargs={'slug': self.slug})

    def get_image(self):
        try:
            return self.image.url
        except:
            return None

    def get_ad_count(self):
        """Returns the count of classified ads associated with this location."""
        return self.classified_ads.count()

    def save(self):
        if not self.code and not self.slug:
            code = f'ClassifiedLocation-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedLocation, self).save()


class ClassifiedAd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classified_ads')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(ClassifiedCategories, on_delete=models.CASCADE, related_name='classified_ads')
    address = models.CharField(max_length=255, blank=True, null=True)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(ClassifiedLocation, on_delete=models.CASCADE, related_name='classified_ads', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hide_price = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    hide_number = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    whats_app_number = models.CharField(max_length=20, blank=True, null=True)
    whats_app_hide_number = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    startTime = models.DateTimeField(blank=True, null=True)
    endTime = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    negotiable = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_premium = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_urgent = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_promoted = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_top = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_bottom = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_left = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_right = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_slider = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_banner = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_category = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_search = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_home = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured_sidebar = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    expired = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_ads', blank=True)
    like = models.PositiveIntegerField(default=0)  # Kept for compatibility; consider removing if unused
    status = models.CharField(max_length=20, choices=Ad_Status, default='New', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_front_url(self):
        return reverse('home:FrontClassifiedAdDetail', kwargs={'slug': self.slug})

    def get_image(self):
        try:
            return self.image.url
        except:
            return None

    def get_map(self):
        """
        Generates a direct Google Maps URL for the object's coordinates.
        This link will open Google Maps with a pin at the specified location.
        """
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        return None

    def get_incremented_views(self):
        """
        Increments the view count for the classified ad.
        """
        self.views += 1
        self.save()

    def get_like_count(self):
        """
        Returns the number of likes for the classified ad.
        """
        return self.likes.count()

    def get_incremented_likes(self):
        """
        Updates the like field to match the current number of likes (optional, if like field is used).
        """
        self.like = self.likes.count()
        self.save()
    def save(self):
        if not self.code and not self.slug:
            code = f'ClassifiedAd-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedAd, self).save()

class ClassifiedAdItem(models.Model):
    classified_ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=100, choices=ClassifiedAd_Type, default='Item')
    item_name = models.CharField(max_length=255)
    item_description = models.TextField(blank=True, null=True)

    item_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    item_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='classified_ad_items', blank=True, null=True)
    item_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    is_extra = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_featured = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_premium = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)


    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_type

    def save(self):
        if not self.code and not self.slug:
            code = f'ClassifiedAdItem{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedAdItem, self).save()

class ClassifiedMedia(models.Model):
    owner_model = models.ForeignKey(ContentType,related_name='classified_media', on_delete=models.CASCADE,null=True, blank=True)
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
            code= f'ClassifiedMedia-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedMedia, self).save(*args, **kwargs)

class AdAttribute(models.Model):
    classified_ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    value = JSONField()
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value}"

    def save(self):
        if not self.code and not self.slug:
            code = f'AdAttribute{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AdAttribute, self).save()

class PromotedClassifiedAd(models.Model):
    ads = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE, related_name='promoted_ads')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ads_type = models.CharField(max_length=20, choices=Ad_Type, default='Normal', null=True, blank=True)
    category = models.CharField(max_length=20, choices=Ad_Category, default='General', null=True, blank=True)
    startTime = models.DateTimeField(blank=True, null=True)
    endTime = models.DateTimeField(blank=True, null=True)
    re_post = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    re_post_time = models.DateTimeField(blank=True, null=True)
    re_post_count = models.PositiveIntegerField(default=0)
    expired = models.CharField(max_length=20, choices=Public_Status, default='Yes', null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=Payment_Status, default='Pending', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Ad_Status, default='New', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self):
        if not self.code and not self.slug:
            code = f'PromotedClassifiedAd-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PromotedClassifiedAd, self).save()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    classified_ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE, related_name='favorites', blank=True, null=True)
    hidden = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.classified_ad.title if self.classified_ad else self.classified_job.title}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'FAV{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Favorite, self).save(*args, **kwargs)


class ClassifiedReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classified_reviews')
    classified_ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE, related_name='classified_reviews', blank=True, null=True)

    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"

    def save(self):
        if not self.code and not self.slug:
            code = f'ClassifiedReview-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedReview, self).save()

class ClassifiedReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classified_reports')
    classified_ad = models.ForeignKey(ClassifiedAd, on_delete=models.CASCADE, related_name='classified_reports', blank=True, null=True)
    reason = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.reason}"

    def save(self):
        if not self.code and not self.slug:
            code = f'ClassifiedReport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedReport, self).save()

class ClassifiedTips(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self):
        if not self.code and not self.slug:
            code = f'ClassifiedTips-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ClassifiedTips, self).save()

class UserSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_searches')
    search_query = models.JSONField(blank=True, null=True)  # Store search parameters as JSON
    search_type = models.CharField(max_length=50, choices=[('ad', 'Ad'), ('job', 'Job')], default='ad')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)

    def __str__(self):
        return f"{self.user.username} - {self.search_query}"

    def save(self):
        if not self.code and not self.slug:
            code = f'UserSearch-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(UserSearch, self).save()

class UserSavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_saved_searches')
    search_query = models.JSONField(blank=True, null=True)  # Store search parameters as JSON
    search_type = models.CharField(max_length=50, choices=[('ad', 'Ad'), ('job', 'Job')], default='ad')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)

    def __str__(self):
        return f"{self.user.username} - {self.search_query}"

    def save(self):
        if not self.code and not self.slug:
            code = f'UserSavedSearch-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(UserSavedSearch, self).save()


class Commercials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commercials')
    title = models.CharField(max_length=255)
    description = models.TextField( blank=True, null=True)
    category = models.ForeignKey(ClassifiedCategories, on_delete=models.CASCADE, related_name='commercials', blank=True, null=True)
    location = models.ForeignKey(ClassifiedLocation, on_delete=models.CASCADE, related_name='commercials', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hide_price = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    hide_number = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    whats_app_number = models.CharField(max_length=20, blank=True, null=True)
    whats_app_hide_number = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    startTime = models.DateTimeField(blank=True, null=True)
    endTime = models.DateTimeField(blank=True, null=True)
    re_post = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    re_post_time = models.DateTimeField(blank=True, null=True)
    re_post_count = models.PositiveIntegerField(default=0)
    is_featured = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    is_premium = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    paid = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Ad_Status, default='New', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self):
        if not self.code and not self.slug:
            code = f'Commercials-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Commercials, self).save()