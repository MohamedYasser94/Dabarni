import logging
from rest_framework import serializers
from core.models.notifications import MobileNotification
from apps.classified.models.models import JobCategories,Job,JobMedia,JobProvider,JobOffer,JobNegotiate,JobProgress,JobReview,JobReviewMedia

logger = logging.getLogger(__name__)


class JobCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategories
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class JobMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobMedia
        fields = '__all__'

class JobProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProvider
        fields = '__all__'

class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'


class JobNegotiateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobNegotiate
        fields = '__all__'


# A simple serializer for the seller/provider's name
class JobProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProgress
        fields = '__all__'

class JobReviewMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = JobReviewMedia
        fields = '__all__'

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class JobReviewSerializer(serializers.ModelSerializer):
    review_media = JobReviewMediaSerializer(source='media', many=True, read_only=True)
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    customer_image = serializers.SerializerMethodField()

    class Meta:
        model = JobReview
        fields = [
            'id','customer_name','customer_image','rating','comment','status',
            'code','slug','create_at','update_at','user','job','review_media' 
        ]
    
    def get_customer_image(self, obj):
        request = self.context.get('request')
        if obj.user.image and request:
            return request.build_absolute_uri(obj.user.image.url)
        return None


class JobOfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for a provider to make a new offer on a job.
    """
    class Meta:
        model = JobOffer
        fields = ['job', 'price']
        read_only_fields = ['provider']

class JobProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProgress
        fields = '__all__'
        

class ProviderNegotiateCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for a provider to make a new negotiation offer.
    """
    class Meta:
        model = JobNegotiate
        fields = ['provider_price']

    def validate_provider_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("السعر يجب أن يكون أكبر من الصفر.")
        return value

class MobileNotificationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source='message')
    type = serializers.CharField(source='notification_type')
    date = serializers.DateTimeField(source='created', format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = MobileNotification
        fields = ['id','title','content','type','date','status',]
