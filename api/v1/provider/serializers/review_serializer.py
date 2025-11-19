# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\provider\serializers\jop_provider_serializer.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.classified.models.models import JobProvider, JobCategories, JobReview
from django.db.models import Avg

User = get_user_model()


class ProviderReviewSerializer(serializers.ModelSerializer):
    """
    Serializer to display a review for a provider.
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = JobReview
        fields = ['id', 'user_name', 'rating', 'comment', 'create_at']


class ProviderProfileWithReviewsDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to display a full provider profile, including related user data and reviews.
    """
    user_image = serializers.ImageField(source='user.image', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    category_title = serializers.CharField(source='category.title', read_only=True)

    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

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
        avg = JobReview.objects.filter(job__customer=obj.user).aggregate(average=Avg('rating'))
        return round(avg['average'], 2) if avg['average'] else 0.0

    def get_reviews(self, obj):
        reviews = JobReview.objects.filter(job__customer=obj.user).order_by('-create_at')[:10]
        return ProviderReviewSerializer(reviews, many=True).data    