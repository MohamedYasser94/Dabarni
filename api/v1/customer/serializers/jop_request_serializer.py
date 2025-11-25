from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.classified.models.models import Job, JobCategories, JobMedia, JobNegotiate, JobOffer, JobProgress
from user.models import UserAddress
from django.utils import timezone
from django.db import transaction
from apps.classified.models.models import JobNegotiate

User = get_user_model()

class JobCategorySerializer(serializers.ModelSerializer):
    """
    Serializer to display full JobCategory details.
    """
    class Meta:
        model = JobCategories
        fields = ['id','title', 'slug', 'image', 'color']

class UserAddressSerializer(serializers.ModelSerializer):
    """
    Serializer to display full UserAddress details.
    """
    class Meta:
        model = UserAddress
        fields = '__all__' 


class JobProgressSerializer(serializers.ModelSerializer):
    """
    Serializer to display details of a JobProgress object.
    Shows provider details ONLY if status is Assigned, In Progress, or Completed.
    """
    providerId = serializers.SerializerMethodField()
    providerName = serializers.SerializerMethodField()
    providerPhone = serializers.SerializerMethodField()
    provider_image = serializers.SerializerMethodField()

    class Meta:
        model = JobProgress
        fields = [
            'id', 'progress_status', 'reason', 'total_cost', 'start_at', 
            'canceled_at', 'canceled_by','providerId','providerName','provider_image','providerPhone'
        ]

    def _should_show_provider_info(self, obj):
        allowed_statuses = ['Assigned', 'In Progress', 'Completed']
        return obj.progress_status in allowed_statuses

    def get_providerId(self, obj):
        if self._should_show_provider_info(obj) and obj.provider:
            return obj.provider.id
        return None

    def get_providerName(self, obj):
        if self._should_show_provider_info(obj) and obj.provider:
            if obj.provider.first_name or obj.provider.last_name:
                return f'{obj.provider.first_name or ""} {obj.provider.last_name or ""}'.strip()
            return obj.provider.username
        return None

    def get_providerPhone(self, obj):
        if self._should_show_provider_info(obj) and obj.provider and hasattr(obj.provider, 'phone'):
             return obj.provider.phone
        return None

    def get_provider_image(self, obj):
        if self._should_show_provider_info(obj) and obj.provider:
            request = self.context.get('request')
            if obj.provider.image:
                return request.build_absolute_uri(obj.provider.image.url) if request else obj.provider.image.url
        return None


class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Job. This serializer is for INPUT (POST requests).
    It handles multipart/form-data with file uploads.
    """
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)
    images = serializers.ListField(
        child=serializers.FileField(max_length=1000, allow_empty_file=False),
        write_only=True,
        required=False,
        help_text="A list of images to upload for the job."
    )
    
    video = serializers.FileField(
        write_only=True,
        required=False,
        help_text="The video file to upload for the job."
    )
    
    category = serializers.SlugRelatedField(
        queryset=JobCategories.objects.all(),
        slug_field='title',
        help_text="The slug of the job category."
    )
    
    location = serializers.SlugRelatedField(
        queryset=UserAddress.objects.all(),
        slug_field='slug',
        help_text="The slug of the user's address for the job location."
    )

    class Meta:
        model = Job
        fields = [
            "id", "title", "description", "quantity", "price",
            "category", "location", "images", "video", "scheduled_at"
        ]
        
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        video_data = validated_data.pop("video", None)
        
        customer_user = self.context.get('request').user

        if not validated_data.get('title'):
            validated_data['title'] = "No Title"

        job = Job.objects.create(customer=customer_user, **validated_data)

        
        
        # Create a JobProgress instance with the initial budget and start_at date
        JobProgress.objects.create(
            job=job,
            customer=customer_user,
            progress_status='Pending',
            total_cost=job.price,
            start_at=None
        )
        
        for image_file in images_data:
            JobMedia.objects.create(job=job, image=image_file)
            
        if video_data:
            JobMedia.objects.create(job=job, video=video_data)
            
        return job


class ProviderOfferSerializer(serializers.ModelSerializer):
    """
    Serializer to display all details of a job offer, including provider's info + progressId.
    """
    providerId = serializers.IntegerField(source='provider.id', read_only=True)
    providerName = serializers.CharField(source='provider.user.get_full_name', read_only=True)
    providerPhone = serializers.CharField(source='provider.user.phone', read_only=True)
    provider_accepted = serializers.BooleanField(read_only=True)
    customer_accepted = serializers.BooleanField(read_only=True)
    progressId = serializers.SerializerMethodField()  
    provider_image = serializers.SerializerMethodField()
    provider_category = serializers.SerializerMethodField()
    provider_rating = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = [
            'id',
            'providerId',
            'providerName',
            'provider_image',
            'provider_category',
            'provider_rating',
            'providerPhone',
            'price',
            'status',
            'create_at',
            'provider_accepted',
            'customer_accepted',
            'progressId',
        ]

    def get_progressId(self, obj):
        if hasattr(obj, 'progresses') and obj.progresses.exists():
            return obj.progresses.first().id
        return None
    
    def get_provider_image(self, obj):
        request = self.context.get('request')
        if obj.provider.user and obj.provider.user.image:
            return request.build_absolute_uri(obj.provider.user.image.url) if request else obj.provider.user.image.url
        return None

    def get_provider_category(self, obj):
        if obj.provider.category:
            return obj.provider.category.title
        return None

    def get_provider_rating(self, obj):
        if hasattr(obj.provider, 'average_rating'):
            return obj.provider.average_rating
        return 0.0





class JobNegotiateSerializer(serializers.ModelSerializer):
    """
    Serializer to display negotiation details with provider info.
    """
    provider_id = serializers.IntegerField(source='provider.id', read_only=True)
    provider_name = serializers.CharField(source='provider.user.get_full_name', read_only=True)
    provider_phone = serializers.CharField(source='provider.user.phone', read_only=True)
    provider_image = serializers.SerializerMethodField()
    provider_category = serializers.SerializerMethodField()
    provider_rating = serializers.SerializerMethodField()

    class Meta:
        model = JobNegotiate
        fields = [
            'id',
            'provider_id','provider_name','provider_phone','provider_image','provider_category','provider_rating',
            'provider_price','customer_price', 'provider_accepted','customer_accepted',
            'code','slug','create_at','update_at','job','offer','customer',
        ]

    def get_provider_image(self, obj):
        request = self.context.get('request')
        if obj.provider.user and obj.provider.user.image:
            return request.build_absolute_uri(obj.provider.user.image.url) if request else obj.provider.user.image.url
        return None

    def get_provider_category(self, obj):
        if obj.provider.category:
            return obj.provider.category.title
        return None

    def get_provider_rating(self, obj):
        if hasattr(obj.provider, 'average_rating'):
            return obj.provider.average_rating
        return 0.0
    

class JobCategorySerializer(serializers.ModelSerializer):
    """
    Serializer to display full JobCategory details.
    """
    class Meta:
        model = JobCategories
        fields = ['id','title', 'slug', 'image', 'color']

class UserAddressSerializer(serializers.ModelSerializer):
    """
    Serializer to display full UserAddress details.
    """
    class Meta:
        model = UserAddress
        fields = '__all__' 

# class JobProgressSerializer(serializers.ModelSerializer):
#     """
#     Serializer to display details of a JobProgress object.
#     """
#     class Meta:
#         model = JobProgress
#         fields = ['id', 'progress_status','reason','total_cost', 'start_at', 'canceled_at', 'canceled_by']

class JobMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for a Job's media to be displayed in the response.
    """
    # Use a custom field to ensure the full URL is returned
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = JobMedia
        # Include 'image' in the fields to ensure it's loaded from the model
        fields = ['id', 'image_url', 'video', 'video_cover', 'file', 'type']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class JobDetailSerializer(serializers.ModelSerializer):
    category = JobCategorySerializer(read_only=True)
    location = UserAddressSerializer(read_only=True)
    title = serializers.CharField(allow_blank=True, default="بدون عنوان")
    # The updated serializer is used here
    media = JobMediaSerializer(many=True, read_only=True)
    progresses = JobProgressSerializer(many=True, read_only=True)
    offers = ProviderOfferSerializer(many=True, read_only=True) 
    negotiations = JobNegotiateSerializer(many=True, read_only=True, source='negotiates')
    customer_name = serializers.SerializerMethodField()
    customer_image = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id","title","description","customer_name", "customer_image",
            "quantity","price", "category","location","media","scheduled_at",
            "progresses","offers","negotiations","views",
            "code","slug","create_at" ,
        ]
    
    def get_customer_name(self, obj):
        if obj.customer:
            if obj.customer.first_name or obj.customer.last_name:
                return f'{obj.customer.first_name or ""} {obj.customer.last_name or ""}'.strip()
            return obj.customer.email
        return "مستخدم غير معروف"

    def get_customer_image(self, obj):
        request = self.context.get('request')
        if obj.customer and obj.customer.image:
            return request.build_absolute_uri(obj.customer.image.url) if request else obj.customer.image.url
        return None



class JobNegotiateCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for a customer to make a new negotiation offer.
    """
    class Meta:
        model = JobNegotiate
        fields = ['customer_price']

    def validate_customer_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("السعر يجب أن يكون أكبر من الصفر.")
        return value
    
class JobNegotiateListSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.first_name', read_only=True) # أو أي حقل للاسم
    offer_price = serializers.DecimalField(source='offer.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = JobNegotiate
        fields = [
            'id', 'offer','provider','provider_name',
            'offer_price','customer_price','provider_accepted',
            'customer_accepted','create_at','update_at'
        ]

class JobNegotiateListSerializer(serializers.ModelSerializer):
    provider_id = serializers.IntegerField(source='provider.id', read_only=True)
    provider_name = serializers.CharField(source='provider.first_name', read_only=True) # أو get_full_name()
    provider_phone = serializers.CharField(source='provider.phone', read_only=True) # تأكد أن حقل الهاتف موجود في موديل المستخدم
    provider_image = serializers.SerializerMethodField()
    provider_category = serializers.CharField(source='provider.category', read_only=True) 
    provider_rating = serializers.SerializerMethodField()
    provider_price = serializers.DecimalField(source='offer.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = JobNegotiate
        fields = [
            'id','provider_id','provider_name','provider_phone','provider_image','provider_category','provider_rating','provider_price',
            'customer_price','provider_accepted','customer_accepted','code','slug','create_at','update_at',
            'job','offer','customer'
        ]

    def get_provider_image(self, obj):
        request = self.context.get('request')
        if obj.provider.user and obj.provider.user.image:
            return request.build_absolute_uri(obj.provider.user.image.url) if request else obj.provider.user.image.url
        return None

    def get_provider_rating(self, obj):
        if hasattr(obj.provider, 'average_rating'):
            return obj.provider.average_rating
        return 0.0