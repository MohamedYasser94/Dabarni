from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from apps.classified.models.classified import *


class ClassifiedCategoriesSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedCategories
        fields = [
            'id', 'title', 'keyword', 'image', 'color', 'job_category',
            'status', 'code', 'slug', 'create_at', 'update_at',
            'lft', 'rght', 'tree_id', 'level', 'parent', 'subcategories'
        ]

    def get_subcategories(self, obj):
        # Return empty list if no subcategories
        return ClassifiedCategoriesSerializer(
            obj.get_children().filter(status='Active'), many=True
        ).data if obj.get_children().exists() else []

class ClassifiedCategoriesWithItemSerializer(serializers.ModelSerializer):
    section_data = serializers.SerializerMethodField()
    total_data = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedCategories
        fields = ['id', 'title', 'total_data', 'style', 'section_data']

    def get_section_data(self, obj):
        items = ClassifiedAd.objects.filter(
            category=obj,
            status='Active',
            is_featured='Yes'
        )
        return ClassifiedAdItemSerializer(items, many=True, context=self.context).data

    def get_total_data(self, obj):
        return ClassifiedAd.objects.filter(
            category=obj,
            status='Active',
            is_featured='Yes'
        ).count()

    def get_style(self, obj):
        style_map = {
            'ministry': 'style_1',
        }
        return style_map.get(obj.title.lower(), 'style_1')



class ClassifiedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedLocation
        fields = '__all__'

class ClassifiedAdItemSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    gallery_images = serializers.SerializerMethodField()
    custom_fields = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = ClassifiedAd
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'image', 'latitude',
            'longitude', 'address', 'number', 'views', 'total_likes', 'status',
            'is_featured', 'create_at', 'user', 'gallery_images', 'custom_fields',
            'category', 'user_id', 'category_id'
        ]

    def get_user(self, obj):
        user = obj.user
        return {
            'id': user.id,
            'name': user.get_full_name() or user.email,
            'phone': user.phone,
            'email': user.email,
            'access_level': user.access_level,
            'image': self.context['request'].build_absolute_uri(user.image.url) if user.image else None,
            'fcm_token': user.fcm_token,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
        } if user else None

    def get_gallery_images(self, obj):
        from django.contrib.contenttypes.models import ContentType
        media = ClassifiedMedia.objects.filter(
            owner_model=ContentType.objects.get_for_model(ClassifiedAd),
            owner_id=obj.id
        )
        return [{
            'id': item.id,
            'image': self.context['request'].build_absolute_uri(item.image.url) if item.image else item.image_url,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat(),
            'item_id': item.owner_id
        } for item in media]

    def get_custom_fields(self, obj):
        attributes = obj.attributes.filter(status='Active')
        return [{
            'id': attr.id,
            'name': attr.name,
            'value': attr.value,
            'type': 'json',
        } for attr in attributes]

    def get_category(self, obj):
        category = obj.category
        return {
            'id': category.id,
            'title': category.title,
            'image': self.context['request'].build_absolute_uri(category.image.url) if category.image else None,
            'create_at': category.create_at.isoformat(),
        } if category else None

    def get_total_likes(self, obj):
        return obj.get_like_count() if hasattr(obj, 'get_like_count') else 0

    def get_user_id(self, obj):
        return obj.user.id if obj.user else None

    def get_category_id(self, obj):
        return obj.category.id if obj.category else None

class ClassifiedAdSerializer(serializers.ModelSerializer):


    class Meta:
        model = ClassifiedAd
        fields = '__all__'

class ClassifiedMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedMedia
        fields = '__all__'


class AdAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdAttribute
        fields = '__all__'


class PromotedClassifiedAdSerializer(serializers.ModelSerializer):


    class Meta:
        model = PromotedClassifiedAd
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class ClassifiedReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedReview
        fields = '__all__'

class ClassifiedReportReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedReport
        fields = '__all__'
class ClassifiedTipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifiedTips
        fields = '__all__'
class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSearch
        fields = '__all__'

class UserSavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSavedSearch
        fields = '__all__'


class CommercialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commercials
        fields = '__all__'




