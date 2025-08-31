
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.crypto import get_random_string
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify


from helper.modelHelper import *
from helper.viewHelper import get_file_path
from user.models import UserAddress

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


class Job(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.IntegerField()
    category = models.ForeignKey(JobCategories, on_delete=models.CASCADE, related_name='jobs')
    location = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='jobs', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    scheduled_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
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
        Calculates and updates the average rating and review count for the provider.
        """
        # Use Django's aggregation to get the average and count efficiently
        agg_data = self.reviews.aggregate(average=Avg('rating'), count=Count('id'))

        self.average_rating = agg_data['average'] or 0.00
        self.review_count = agg_data['count'] or 0
        self.save()

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Job{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        # Pass all arguments to the parent save method
        super(Job, self).save(*args, **kwargs)

class JobMedia(models.Model):
    job= models.ForeignKey(Job, on_delete=models.CASCADE, related_name='media')
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


class JobProvider(models.Model):
    # --- RELATIONSHIP ---
    # A user can only have one provider profile.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_provider_profile')

    # --- PROFESSIONAL DETAILS ---
    category = models.ForeignKey(JobCategories, on_delete=models.CASCADE, related_name='job_providers')
    experience_years = models.IntegerField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)  # Renamed from pio for clarity
    website = models.URLField(blank=True, null=True)

    # --- BUSINESS CONTACT & LOCATION ---
    business_phone = models.CharField(max_length=20, blank=True, null=True)  # Renamed from 'number'
    address = models.TextField(blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)

    # --- BUSINESS REGISTRATION & DOCUMENTS ---
    commercial_number = models.CharField(max_length=100, blank=True, null=True)
    commercial_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    commercial_image2 = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    vat_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    license_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)

    # --- FINANCIAL ---
    bank_account = models.CharField(max_length=50, blank=True, null=True)

    # --- SYSTEM & STATUS FIELDS ---
    data_progress = models.IntegerField(blank=True, null=True)
    data_confirmed = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    # --- REMOVED FIELDS (Now in User or UserProfile) ---
    # id_number, id_image_front, id_image_back, residence_image, number, etc.

    def __str__(self):
        # Display the company name or the user's name.
        return self.company or self.user.get_full_name()

    @property
    def total_spent(self):
        # This property to calculate costs is good.
        return sum(job.cost or 0 for job in self.jobs.all())

    @property
    def profile_completion_percentage(self):
        """
        Calculates the profile completion percentage based on a weighted system.
        """
        total_percentage = 0

        # --- Category 1: Personal Data (Weight: 25%) ---
        # These fields are on the related User and UserProfile models
        try:
            profile = self.user.profile
            personal_data_fields = [
                self.user.first_name, self.user.last_name, self.user.email, self.user.phone,
                profile.dob, profile.nationality, profile.residence
            ]
            personal_weight = 25 / len(personal_data_fields)
            completed_personal = sum(1 for field in personal_data_fields if field)
            total_percentage += completed_personal * personal_weight
        except self.user.profile.__class__.DoesNotExist:
            pass  # No profile, no points for this section

        # --- Category 2: Job Details (Weight: 25%) ---
        job_details_fields = [self.category, self.experience_years, self.company, self.business_phone, self.address]
        job_weight = 25 / len(job_details_fields)
        completed_job = sum(1 for field in job_details_fields if field)
        total_percentage += completed_job * job_weight

        # --- Category 3: Bio (Weight: 25%) ---
        if self.bio and self.bio.strip():
            total_percentage += 25

        # --- Category 4: Documents (Weight: 25%) ---
        # Documents are on both UserProfile and JobProvider
        completed_docs = 0
        document_fields = [
            self.commercial_image, self.vat_image, self.license_image, self.commercial_image2
        ]

        # Check JobProvider documents
        completed_docs += sum(1 for field in document_fields if field)

        # Check UserProfile documents
        try:
            profile = self.user.profile
            profile_docs = [profile.id_image_front, profile.id_image_back, profile.residence_image]
            completed_docs += sum(1 for field in profile_docs if field)
            total_docs = len(document_fields) + len(profile_docs)
        except self.user.profile.__class__.DoesNotExist:
            total_docs = len(document_fields)  # Only count provider docs if no profile exists

        if total_docs > 0:
            doc_weight = 25 / total_docs
            total_percentage += completed_docs * doc_weight

        return int(total_percentage)

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'JobProvider-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super().save(*args, **kwargs)  # Use modern super() syntax

class JobOffer(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='offers')
    provider = models.ForeignKey(JobProvider, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Job_Offer_Status, default='New', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.request.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'JobOffer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super().save(*args, **kwargs)

class JobNegotiate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='negotiates')
    offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='negotiations')
    provider = models.ForeignKey(JobProvider, on_delete=models.CASCADE, related_name='negotiations')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='negotiations')
    provider_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    customer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    provider_accepted = models.BooleanField(default=False)
    customer_accepted = models.BooleanField(default=False)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.request.user.username} - {self.price}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'JobNogotiable-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super().save(*args, **kwargs)

class JobProgress(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='progresses')
    offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='progresses', blank=True, null=True)
    provider = models.ForeignKey(JobProvider, on_delete=models.CASCADE, related_name='progresses',blank=True,null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_progresses')
    extra_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    extra_request_time = models.DateTimeField(blank=True, null=True)
    extra_approved_time = models.DateTimeField(blank=True, null=True)
    extra_request = models.TextField(blank=True, null=True)
    extra_cost_approved = models.BooleanField(default=False)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    progress_status = models.CharField(max_length=20, choices=Job_Progress_Status, default='Pending', null=True, blank=True)
    provider_progress = models.TextField(blank=True, null=True)
    customer_progress = models.TextField(blank=True, null=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    canceled_at = models.DateTimeField(blank=True, null=True)
    canceled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='canceled_jobs',null=True,blank=True)
    cancel_system_approved = models.BooleanField(default=False)
    cancel_system_decision = models.TextField(blank=True, null=True)
    cancel_provider_approved = models.BooleanField(default=False)
    cancel_customer_approved = models.BooleanField(default=False)
    cancel_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cancel_cost_for_provider = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cancel_cost_for_customer = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cancel_approved_at = models.DateTimeField(blank=True, null=True)
    cancel_approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_cancellations', blank=True, null=True)
    cancel_approved_reason = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=Payment_Status, default='Pending', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.request.user.username} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'JobProgress-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super().save(*args, **kwargs)

class JobReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_reviews')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_reviews', blank=True, null=True)
    rating = models.PositiveIntegerField(default=0)
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

class JobReviewMedia(models.Model):
    review = models.ForeignKey(JobReview, on_delete=models.CASCADE, related_name='media')
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
            code= f'JobReviewMedia-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(JobReviewMedia, self).save(*args, **kwargs)





