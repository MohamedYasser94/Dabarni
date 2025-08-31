# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\provider\serializers\category_serializers.py
from rest_framework import serializers
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from apps.classified.models.models import JobCategories

class JobCategorySerializer(serializers.ModelSerializer):
    """
    Serializer to represent a category in a tree structure.
    """
    children = serializers.SerializerMethodField()

    class Meta:
        model = JobCategories
        fields = ['id', 'title', 'slug', 'image', 'color', 'children']
    
    def get_children(self, obj):
        # Recursively serialize the children
        children = obj.get_children().filter(status='Active')
        return JobCategorySerializer(children, many=True).data