import logging

from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from rest_framework import serializers
from slugify import slugify

from Dabarni import settings
from api.v1.serializers.app.ticket import ServiceReviewSerializer
from apps.classified.models.job import JobCategories,JobLocation, JobProvider, Job, JobRequirement,JobRequest,JobRequestDocument,JobMedia,JobReview
from apps.classified.models.ticket import ServiceReview

logger = logging.getLogger(__name__)

# A simple serializer for the seller/provider's name
class JobProviderNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProvider
        fields = ['name']

# Serializer for the reviews to calculate the average rating
class JobReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReview
        fields = ['rating']
class SellerForMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProvider
        fields = ['name']

class ReviewsForMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReview
        fields = ['rating']
# The main serializer for your Job model for the search results
class JobSearchSerializer(serializers.ModelSerializer):
    seller_for_mobile = SellerForMobileSerializer(source='provider')


    class Meta:
        model = Job
        fields = '__all__'



    def get_image_url(self, obj):
        return obj.get_image() if obj.image else None

# Serializer for subcategories
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategories # Your MPTT model handles both categories and subcategories
        fields = ['id', 'title']


class JobCategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobCategories
        fields = '__all__'


class JobLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobLocation
        fields = '__all__'

class JobProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobProvider
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    requirements = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    provider_slug = serializers.SlugField(source='provider.slug', read_only=True)

    # To send the provider's name directly
    provider_name = serializers.CharField(source='provider.name', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

    def get_requirements(self, obj):
        # Corrected the filter to use 'classified_job'
        requirements = JobRequirement.objects.filter(classified_job=obj)
        return JobRequirementSerializer(requirements, many=True).data

    def get_media(self, obj):
        # Assuming the related name on JobMedia for the GenericForeignKey is 'job_media'
        # and you want to filter based on the Job object's content type and id.
        media = JobMedia.objects.filter(owner_model=ContentType.objects.get_for_model(obj), owner_id=obj.id)
        return JobMediaSerializer(media, many=True).data

    def get_reviews(self, obj):
        reviews = JobReview.objects.filter(classified_job=obj)
        return JobReviewSerializer(reviews, many=True).data

class JobDetailsSerializer(serializers.ModelSerializer):
    requirements = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    # To send the provider's name directly
    provider_name = serializers.CharField(source='provider.name', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'

    def get_requirements(self, obj):
        # Corrected the filter to use 'classified_job'
        requirements = JobRequirement.objects.filter(classified_job=obj)
        return JobRequirementSerializer(requirements, many=True).data

    def get_media(self, obj):
        # Assuming the related name on JobMedia for the GenericForeignKey is 'job_media'
        # and you want to filter based on the Job object's content type and id.
        media = JobMedia.objects.filter(owner_model=ContentType.objects.get_for_model(obj), owner_id=obj.id)
        return JobMediaSerializer(media, many=True).data

    def get_provider(self, obj):
        provider = JobProvider.objects.filter(id=obj.provider_id).first()
        if provider:
            return JobProviderSerializer(provider).data
        return None

    def get_reviews(self, obj):
        reviews = ServiceReview.objects.filter(job=obj)
        return ServiceReviewSerializer(reviews, many=True).data

class JobRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequirement
        fields = '__all__'

class JobRequestSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = JobRequest
        fields = '__all__'
        read_only_fields = ( 'code', 'slug')

    def get_documents(self, obj):
        documents = JobRequestDocument.objects.filter(classified_job_request=obj)
        paytabs_config = serializers.SerializerMethodField()
        return JobRequestDocumentSerializer(documents, many=True).data

    def get_paytabs_config(self, obj):
        return {
            'paytabs_url': 'https://secure-egypt.paytabs.com/payment/request',
            'profile_id': settings.PAYTABS_PROFILE_ID,
            'callback_url': settings.PAYTABS_CALLBACK_URL,
            'return_url': settings.PAYTABS_RETURN_URL,
            # Optionally include server_key (less secure, see alternative below)
            'server_key': settings.PAYTABS_SERVER_KEY,
        }

class JobRequestDetailsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField()

    class Meta:
        model = JobRequest
        fields = '__all__'
        read_only_fields = ( 'code', 'slug')

    def get_documents(self, obj):
        documents = JobRequestDocument.objects.filter(classified_job_request=obj)
        paytabs_config = serializers.SerializerMethodField()
        return JobRequestDocumentSerializer(documents, many=True).data

    def get_job(self, obj):
        job = Job.objects.filter(id=obj.classified_job.id).first()
        if job:
            return JobDetailsSerializer(job).data
        return None

    def get_provider(self, obj):
        provider = JobProvider.objects.filter(id=obj.classified_job.provider_id).first()
        if provider:
            return JobProviderSerializer(provider).data
        return None


class JobRequestDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequestDocument
        fields = '__all__'

class JobMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobMedia
        fields = '__all__'
