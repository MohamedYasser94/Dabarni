from rest_framework import serializers
from apps.classified.models.models import Job, JobMedia

class JobMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for a Job's media to be displayed in the response.
    """
    # Use this SerializerMethodField to return the correct URL for the image
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JobMedia
        fields = ['id', 'image_url', 'video', 'video_cover', 'file', 'type']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
