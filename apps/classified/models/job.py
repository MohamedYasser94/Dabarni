
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_providers')
    category = models.ForeignKey(JobCategories, on_delete=models.CASCADE, related_name='job_providers')
    experience_years = models.IntegerField(blank=True, null=True)
    commercial_number = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    pio = models.TextField(blank=True, null=True)
    id_image_front = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    id_image_back = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    residence_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    commercial_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    commercial_image2 = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    vat_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    license_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    location_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    address_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    address_video = models.URLField(blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True)
    proof_number = models.CharField(max_length=20, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    document_number = models.CharField(max_length=20, blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    data_progress = models.IntegerField(blank=True, null=True)
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
    provider = models.ForeignKey(JobProvider, on_delete=models.CASCADE, related_name='progresses')
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
    canceled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='canceled_jobs')
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





