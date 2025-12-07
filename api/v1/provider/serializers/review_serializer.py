from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.classified.models.models import JobProvider, JobCategories, JobReview, JobReviewMedia
from django.db.models import Avg

User = get_user_model()

class JobReviewMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = JobReviewMedia
        fields = ['id', 'file_url', 'type', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class ProviderReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    media = JobReviewMediaSerializer(many=True, read_only=True)

    class Meta:
        model = JobReview
        fields = [
            'id', 'user_name', 'user_image', 'rating', 'comment', 'create_at', 'media'
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or "مستخدم"

    def get_user_image(self, obj):
        request = self.context.get('request')
        if obj.user.image and request:
            return request.build_absolute_uri(obj.user.image.url)
        return None

class ProviderProfileWithReviewsDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to display a full provider profile, including related user data and reviews.
    Relies on JobProgress to link Jobs to Providers.
    """
    user_image = serializers.SerializerMethodField()
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    category_title = serializers.CharField(source='category.title', read_only=True)
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    commercial_image = serializers.SerializerMethodField()
    vat_image = serializers.SerializerMethodField()
    license_image = serializers.SerializerMethodField()

    class Meta:
        model = JobProvider
        fields = [
            'id', 'user_image', 'user_first_name', 'user_last_name', 'user_phone',
            'category_title', 'experience_years', 'company', 'bio',
            'address', 'latitude', 'longitude',
            'commercial_image', 'vat_image', 'license_image',
            'profile_completion_percentage', 'average_rating', 'reviews'
        ]

    def get_average_rating(self, obj):
        """
        Calculates average rating based on jobs linked via JobProgress.
        """
        avg = JobReview.objects.filter(
            job__progresses__provider=obj
        ).aggregate(average=Avg('rating'))
        
        return round(avg['average'], 2) if avg['average'] else 0.0

    def get_reviews(self, obj):
        """
        Fetches the latest 10 reviews for jobs done by this provider.
        """
        reviews = JobReview.objects.filter(
            job__progresses__provider=obj
        ).distinct().prefetch_related('media').order_by('-create_at')[:10]

        return ProviderReviewSerializer(reviews, many=True, context=self.context).data

    def get_user_image(self, obj):
        request = self.context.get('request')
        if obj.user.image and request:
            return request.build_absolute_uri(obj.user.image.url)
        return None

    def _get_image_url(self, image_field):
        request = self.context.get('request')
        if image_field and request:
            return request.build_absolute_uri(image_field.url)
        return None

    def get_commercial_image(self, obj):
        return self._get_image_url(obj.commercial_image)

    def get_vat_image(self, obj):
        return self._get_image_url(obj.vat_image)

    def get_license_image(self, obj):
        return self._get_image_url(obj.license_image)