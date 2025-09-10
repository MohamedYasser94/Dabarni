# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\customer\serializers\JobReviewCreateSerializer.py

from rest_framework import serializers
from django.db import transaction
from apps.classified.models.models import JobReview, JobReviewMedia

class JobReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for a customer to create a new review with optional media files.
    """
    review_media = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = JobReview
        fields = ['rating', 'comment', 'review_media']

    def validate_rating(self, value):
        if not 0 <= value <= 5:
            raise serializers.ValidationError("التقييم يجب أن يكون بين 0 و 5.")
        return value
        
    def create(self, validated_data):
        with transaction.atomic():
            user = self.context.get('request').user
            job = self.context.get('job')
            review_media_files = validated_data.pop('review_media', [])
            
            if JobReview.objects.filter(user=user, job=job).exists():
                raise serializers.ValidationError("لقد قمت بتقييم هذه الوظيفة بالفعل.")
                
            review = JobReview.objects.create(
                user=user,
                job=job,
                **validated_data
            )
            
            # Create a JobReviewMedia object for each uploaded file
            for file in review_media_files:
                JobReviewMedia.objects.create(
                    review=review,
                    file=file
                )
            
            # You can add logic here to recalculate the provider's rating
            # after the review is saved.
            
            return review