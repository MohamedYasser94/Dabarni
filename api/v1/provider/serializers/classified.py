import logging

from rest_framework import serializers

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


class JobReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReview
        fields = '__all__'


class JobReviewMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobReviewMedia
        fields = '__all__'