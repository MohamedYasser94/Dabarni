from rest_framework import serializers

from core.models.blog import BlogCategories, BlogArticle


class BlogCategorySerializer(serializers.ModelSerializer):


    class Meta:
        model = BlogCategories
        fields = ['id', 'title', 'image', 'slug']



class BlogArticleSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(source='category.title', read_only=True)
    # You can add an image field here if your Article model has one

    class Meta:
        model = BlogArticle
        fields = [
            'id', 'title', 'slug', 'body',
            'author', 'category_name', 'views','image','create_at'
        ]