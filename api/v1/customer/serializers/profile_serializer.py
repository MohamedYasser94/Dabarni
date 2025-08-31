from rest_framework import serializers
from user.models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    phone = serializers.CharField(source="user.phone", required=False)
    id_image_front = serializers.ImageField(required=False, allow_null=True)
    id_image_back = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = UserProfile
        fields = [
            "first_name", "last_name", "email", "phone",
            "dob", "id_number",  "id_image_front", "id_image_back", "gender",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
