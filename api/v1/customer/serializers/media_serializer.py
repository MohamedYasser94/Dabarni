from rest_framework import serializers
from apps.classified.models.models import Job, JobMedia

class JobMediaSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = JobMedia
        fields = ["id", "image", "video", "image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request", None)
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None

