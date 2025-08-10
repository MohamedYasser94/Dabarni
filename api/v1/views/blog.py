from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response

from api.v1.serializers.blog import *
from core.models.blog import *


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow any user to view news
def ApiBlogCategoryList(request):
    """
    Returns a list of all published blog categories.
    """
    try:
        categories = BlogCategories.objects.filter(status='Active').order_by('id')
        serializer = BlogCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print('das ' ,e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiBlogArticleList(request):
    """
    Returns a list of blog articles.
    - If no 'category_id' is provided, it returns the 10 most recent articles.
    - If a 'category_id' is provided, it returns articles from that category.
    """
    try:
        category_id = request.query_params.get('category_id', None)

        articles = BlogArticle.objects.all().select_related( 'category')

        if category_id:
            articles = articles.filter(category__id=category_id)
        else:
            # If no category is selected, return the 10 most recent articles
            articles = articles.order_by('-create_at')[:10]

        serializer = BlogArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print('das ' ,e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiBlogArticleDetails(request, slug):
    """
    Returns the details of a single blog article, identified by its slug.
    """
    try:
        article = BlogArticle.objects.get(slug=slug, )
        serializer = BlogArticleSerializer(article, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except BlogArticle.DoesNotExist:
        return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def ApiBlogArticleViewed(request, slug):
    """
    Increments the view count for a single blog article.
    """
    try:
        article = BlogArticle.objects.get(slug=slug)
        article.viewed()  # This calls the viewed() method on your model
        return Response({"success": f"View count for article '{slug}' incremented."}, status=status.HTTP_200_OK)
    except BlogArticle.DoesNotExist:
        return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)