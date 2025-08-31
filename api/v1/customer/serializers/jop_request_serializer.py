# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\customer\serializers\jop_request_serializer.py

from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.classified.models.models import Job, JobCategories, JobMedia, JobProgress
from user.models import UserAddress

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

class JobMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for a Job's media to be displayed in the response.
    """
    class Meta:
        model = JobMedia
        fields = ['id','image', 'video', 'video_cover', 'file', 'type']

class JobProgressSerializer(serializers.ModelSerializer):
    """
    Serializer to display details of a JobProgress object.
    """
    class Meta:
        model = JobProgress
        fields = ['id', 'progress_status','reason','total_cost', 'start_at', 'canceled_at', 'canceled_by']

class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Job.
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
        slug_field='slug',
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

        job = Job.objects.create(customer=customer_user, **validated_data)
        
        # Create a JobProgress instance with the initial budget (total_cost) and start_at date
        JobProgress.objects.create(
            job=job,
            customer=customer_user,
            progress_status='Pending',
            total_cost=job.price, # Use the price from the Job as the initial total cost
            start_at=timezone.now()
        )
        
        for image_file in images_data:
            JobMedia.objects.create(job=job, image=image_file)
            
        if video_data:
            JobMedia.objects.create(job=job, video=video_data)
            
        return job

class JobDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to display a Job's details.
    """
    category = JobCategorySerializer(read_only=True)
    location = UserAddressSerializer(read_only=True)
    media = JobMediaSerializer(many=True, read_only=True)
    # Use the new JobProgressSerializer to show the progress details
    progress = JobProgressSerializer(source='progresses', read_only=True, many=True)

    class Meta:
        model = Job
        fields = [
            "id","title", "description", "quantity", "price",
            "category", "location", "media", "scheduled_at",
            "progress", "views", "code", "slug", "create_at"
        ]