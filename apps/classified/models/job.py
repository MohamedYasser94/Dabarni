
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import JSONField, Avg, Count
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


class JobCategories(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=500,)
    keyword = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    color = models.CharField(max_length=20, blank=True, null=True,default='#000000',choices=COLORS)
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


    def get_front_url(self):
        return reverse('home:FrontProviderCategoryDetail', kwargs={'slug': self.slug})


    def get_image(self):
        try:
            return self.image.url
        except:
            return None


    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'JobCategories-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobCategories, self).save(*args, **kwargs)


class JobLocation(models.Model):
    country = models.CharField(max_length=100, blank=True, null=True, choices=Country_List, default='None')
    governorate = models.CharField(max_length=100, blank=True, null=True ,choices=Governorates_List,default='None')
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city}, {self.region}, {self.country}"

    def save(self):
        if not self.code and not self.slug:
            code = f'JobLocation-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobLocation, self).save()

class JobProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_providers')
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=100, choices=JobProvider_Type, default='Company', null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    id_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    document_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    proof_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    location_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    address_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    address_video = models.URLField(blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    proof_number = models.CharField(max_length=20, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    document_number = models.CharField(max_length=20, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    governorate = models.ForeignKey(Governorates, on_delete=models.CASCADE, related_name='job_providers', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    data_confirmed = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_image(self):
        try:
            return self.image.url
        except:
            return None
    @property
    def total_spent(self):
        return sum(job.cost or 0 for job in self.jobs.all())

    def save(self):
        if not self.code and not self.slug:
            code = f'JobProvider-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobProvider, self).save()

class JobProviderEmployee(models.Model):
    provider = models.ForeignKey(JobProvider, on_delete=models.CASCADE, related_name='employees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_provider_employees')
    role = models.CharField(max_length=100, choices=JobProvider_Employee_Role, default='Employee', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.provider.name}"

    def save(self):
        if not self.code and not self.slug:
            code = f'JobProviderEmployee-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobProviderEmployee, self).save()

class Job(models.Model):
    provider = models.ForeignKey(JobProvider, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(JobCategories, on_delete=models.CASCADE, related_name='jobs')
    location = models.ForeignKey(JobLocation, on_delete=models.CASCADE, related_name='jobs', blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_type = models.CharField(max_length=20, choices=ClassifiedJob_Cost_Type, default='Fixed', null=True, blank=True)
    duration = models.CharField(max_length=20, default='One-Day', null=True, blank=True)
    need_requirements = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    is_featured = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    negotiable = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    requested = models.PositiveIntegerField(default=0)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_front_url(self):
        return reverse('home:FrontProviderJobDetail', kwargs={'slug': self.slug})

    def get_image(self):
        try:
            return self.image.url
        except:
            return None

    def update_rating(self):
        """
        Calculates and updates the average rating and review count for the job.
        """
        # Use Django's aggregation to get the average and count efficiently
        agg_data = self.reviews.aggregate(average=Avg('rating'), count=Count('id'))

        self.average_rating = agg_data['average'] or 0.00
        self.review_count = agg_data['count'] or 0
        self.save()

    def save(self):
        if not self.code and not self.slug:
            code = f'Job{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Job, self).save()

class JobRequirement(models.Model):
    classified_job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='requirements')
    requirement_type = models.CharField(max_length=100, choices=ClassifiedJob_Requirement_Type, default='Requirement',blank=True, null=True)
    requirement_name = models.CharField(max_length=100,blank=True, null=True)
    requirement_description = models.TextField(blank=True, null=True)
    is_required = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.requirement_type

    def save(self):
        if not self.code and not self.slug:
            code = f'JobRequirement-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobRequirement, self).save()

    



class JobBenefit(models.Model):
    classified_job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='benefits')
    benefit_type = models.CharField(max_length=100, choices=ClassifiedJob_Benefit_Type, default='Benefit')
    benefit_name = models.CharField(max_length=255)
    benefit_description = models.TextField(blank=True, null=True)
    is_required = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.benefit_type

    def save(self):
        if not self.code and not self.slug:
            code = f'JobBenefit-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobBenefit, self).save()


class JobRequest(models.Model):
    classified_job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_requests')
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to=get_file_path, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    negotiable = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    negotiable_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    negotiable_accepted = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    negotiable_accepted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=Payment_Status, default='Pending', null=True, blank=True)
    progress = models.CharField(max_length=20, choices=ClassifiedJob_Request_Progress, default='Pending', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.classified_job.title}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'JobRequest-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super().save(*args, **kwargs)

class JobRequestDocument(models.Model):
    classified_job_request = models.ForeignKey(JobRequest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=100, choices=ClassifiedJob_Request_Document_Type, default='Document')
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to=get_file_path, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document_type

    def get_file_url(self):
        if self.requirement_file:
            return self.requirement_file.url
        return None

    def save(self):
        if not self.code and not self.slug:
            code = f'JobRequestDocument-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobRequestDocument, self).save()


class JobMedia(models.Model):
    owner_model = models.ForeignKey(ContentType,related_name='job_media', on_delete=models.CASCADE,null=True, blank=True)
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
            code= f'JobMedia-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobMedia, self).save(*args, **kwargs)


class JobReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_reviews')
    classified_job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_reviews', blank=True, null=True)
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
            code = f'JobReview-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobReview, self).save()


