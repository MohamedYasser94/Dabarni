# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\provider\views\category_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from apps.classified.models.models import JobCategories
from api.v1.response import success_response, error_response
from api.v1.customer.serializers.category_serializer import JobCategorySerializer


@extend_schema(
    tags=["Job Categories"],
    responses={200: JobCategorySerializer(many=True), 500: 'Error Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_categories(request):
    """
    API endpoint to list all root job categories in a tree format.
    """
    try:
        # Get all root nodes (categories without a parent) that are active.
        categories = JobCategories.objects.filter(parent__isnull=True, status='Active')
        serializer = JobCategorySerializer(categories, many=True)
        return success_response(
            message="Categories retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve categories",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )

@extend_schema(
    tags=["Job Categories"],
    responses={200: JobCategorySerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_category(request, slug):
    """
    API endpoint to get details of a single category by its slug.
    """
    try:
        # Fetch the category by slug, and if not found, return a 404.
        category = get_object_or_404(JobCategories, slug=slug, status='Active')
        serializer = JobCategorySerializer(category)
        return success_response(
            message="Category retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve category",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )