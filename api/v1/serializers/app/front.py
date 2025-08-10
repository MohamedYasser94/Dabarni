from rest_framework import serializers
from apps.front.models.models import *

class ApiCategorySliderSerializer(serializers.ModelSerializer):
    """
    Serializes a Category object into the format expected by Flutter's CategorySlider.
    """
    # Renaming fields to match the Flutter model
    translated_name = serializers.CharField(source='title')


    class Meta:
        model = FrontCategories
        fields = ['id', 'title', ]




class SliderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slider
        fields = '__all__'

class SliderItemSerializer(serializers.ModelSerializer):
    sequence = serializers.IntegerField(source='order')
    model_type = serializers.CharField(source='type')
    model_id = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()

    class Meta:
        model = SliderItem
        fields = ['id', 'image', 'sequence', 'model_type', 'model_id', 'model']

    def get_model_id(self, obj):
        # Returns the ID of the related model (e.g., Category)
        if obj.type == 'Category' and obj.category:
            return obj.category.id
        # Add other types here if needed
        return None

    def get_model(self, obj):
        # Returns the nested model object (e.g., Category data)
        if obj.type == 'Category' and obj.category:
            # Use the category serializer to format the nested object
            return ApiCategorySliderSerializer(obj.category).data
        # Add other types here if needed
        return None


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BannerItem
        fields = '__all__'


class BannerItemSerializer(serializers.ModelSerializer):
    # title = CommonTranslateSerializer()
    # sub_title = CommonTranslateSerializer()
    # button_text = CommonTranslateSerializer()
    # offers = CommonTranslateSerializer()

    class Meta:
        model = BannerItem
        fields = '__all__'

class FaqSerializer(serializers.ModelSerializer):
    # question = CommonTranslateSerializer()
    # answer = CommonTranslateSerializer()

    class Meta:
        model = Faq
        fields = "__all__"

class PrivacyPolicySerializer(serializers.ModelSerializer):
    # title = CommonTranslateSerializer()
    # sub_title = CommonTranslateSerializer()
    # button_text = CommonTranslateSerializer()
    # offers = CommonTranslateSerializer()

    class Meta:
        model = PrivacyPolicy
        fields = "__all__"



class TermsAndConditionsSerializer(serializers.ModelSerializer):
    # title = CommonTranslateSerializer()
    # sub_title = CommonTranslateSerializer()
    # button_text = CommonTranslateSerializer()
    # offers = CommonTranslateSerializer()

    class Meta:
        model = TermsAndConditions
        fields = "__all__"
