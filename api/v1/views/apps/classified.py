from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.v1.serializers.app.classified import *
from api.v1.serializers.user import UserSerializer
from apps.classified.models.classified import *


@csrf_exempt
def ApiClassifiedCategoryList(request):
    """
    This view provides a paginated list of active classified categories
    to match the Flutter application's FetchCategoryCubit.
    """
    try:
        # Get all active categories, ordered by creation date (descending)
        all_categories = ClassifiedCategories.objects.filter(status='Active',
                                                             parent__isnull=True).order_by('-create_at')

        # Get page number from request, default to 1
        page_number = request.GET.get('page', 1)
        # Set items per page to match Flutter's expectations (adjustable)
        per_page = 10
        paginator = Paginator(all_categories, per_page)

        try:
            # Get the requested page
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver empty page
            return JsonResponse({
                'success': True,
                'message': 'No more categories available',
                'total': paginator.count,
                'categories': [],  # Changed from 'data' to 'categories'
                'page': page_number,
                'has_more': False
            }, status=200)

        # Serialize the data for the current page
        category_serializer = ClassifiedCategoriesSerializer(
            page_obj.object_list,
            many=True,
            context={'request': request}
        )

        # Structure the response to match Flutter's expected format
        data = {
            'success': True,
            'message': 'Success',
            'total': paginator.count,  # Total number of categories
            'categories': category_serializer.data,  # Changed from 'data' to 'categories'
            'page': page_obj.number,  # Current page number
            'has_more': page_obj.has_next()  # Indicate if more pages are available
        }

        return JsonResponse(data, status=200)

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'total': 0,
            'categories': [],  # Changed from 'data' to 'categories'
            'page': page_number,
            'has_more': False
        }, status=500)


@csrf_exempt
def ApiHomeClassifiedFeaturedSection(request):
    """
    Provides a list of active classified categories with their featured items.
    """
    try:
        # Get query parameters
        city = request.GET.get('city')
        area_id = request.GET.get('area_id')
        country = request.GET.get('country')
        state = request.GET.get('state')
        radius = request.GET.get('radius')
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        queryset = ClassifiedCategories.objects.filter(status='Active').order_by('-create_at')

        serializer = ClassifiedCategoriesWithItemSerializer(
            queryset,
            many=True,
            context={'request': request}
        )

        response = {
            'success': True,
            'message': 'Success',
            'data': serializer.data  # Include all categories, even with empty section_data
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': []
        }, status=500)
@csrf_exempt
def ApiHomeClassifiedList(request):
    """
    This view provides a paginated list of active classified ads, matching the Flutter
    application's HomeRepository.fetchHomeAllItems expected response structure.
    """
    try:
        # Get query parameters
        page_number = request.GET.get('page', 1)
        sort_by = request.GET.get('sort_by', 'new-to-old')
        city = request.GET.get('city')
        area_id = request.GET.get('area_id')
        country = request.GET.get('country')
        state = request.GET.get('state')
        radius = request.GET.get('radius')
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        # Base queryset
        queryset = ClassifiedAd.objects.filter(status='Active')

        # Apply filters
        if city:
            queryset = queryset.filter(location__city=city)
        if area_id:
            queryset = queryset.filter(location__area_id=area_id)
        if country:
            queryset = queryset.filter(location__country=country)
        if state:
            queryset = queryset.filter(location__governorate=state)
        # Note: radius, latitude, longitude filtering requires geospatial logic
        # Implement if ClassifiedLocation supports it, e.g., using django.contrib.gis

        # Apply sorting
        if sort_by == 'new-to-old':
            queryset = queryset.order_by('-create_at')
        else:
            queryset = queryset.order_by('create_at')

        # Paginate
        per_page = 10
        paginator = Paginator(queryset, per_page)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            return JsonResponse({
                'success': True,
                'message': 'No more items available',
                'data': {'data': [], 'total': paginator.count}
            }, status=200)

        # Serialize data
        serializer = ClassifiedAdItemSerializer(
            page_obj.object_list,
            many=True,
            context={'request': request}
        )

        response = {
            'success': True,
            'message': 'Success',
            'data': {
                'data': serializer.data,
                'total': paginator.count
            }
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': {'data': [], 'total': 0}
        }, status=500)


@csrf_exempt
def ApiGetReportReasons(request):
    """
    Provides a list of report reasons for classified ads.
    """
    try:
        # Fetch all active report reasons
        report_reasons = ClassifiedReport.objects.filter(status='Active').order_by('create_at')

        # Serialize the data
        serializer = ClassifiedReportReasonSerializer(
            report_reasons,
            many=True,
            context={'request': request}
        )

        response = {
            'success': True,
            'message': 'Success',
            'data': serializer.data
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': []
        }, status=500)


@csrf_exempt
def ApiGetClassifiedTips(request):
    """
    Provides a list of classified tips.
    """
    try:
        # Fetch all active classified tips
        tips = ClassifiedTips.objects.filter(status='Active').order_by('create_at')

        # Serialize the data
        serializer = ClassifiedTipsSerializer(
            tips,
            many=True,
            context={'request': request}
        )

        response = {
            'success': True,
            'message': 'Success',
            'data': serializer.data
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': []
        }, status=500)


@csrf_exempt
def ApiGetClassifiedSeller(request):
    """
    Provides details of the seller for a specific classified ad.
    """
    try:
        # Fetch the classified ad by ID
        id = request.POST.get('id')
        if not id:
            return JsonResponse({
                'success': False,
                'message': 'ID is required',
                'data': {}
            }, status=400)
        classified_ad = ClassifiedAd.objects.filter(id=id, status='Active').first()
        classified_seller = UserSearch.objects.filter(classified_ad=classified_ad).order_by('-create_at').first()
        if not classified_ad:
            return JsonResponse({
                'success': False,
                'message': 'Classified ad not found',
                'data': {}
            }, status=404)

        # Serialize the seller data
        serializer = UserSerializer(
            classified_seller.user if classified_seller else None,
            context={'request': request}
        )

        response = {
            'success': True,
            'message': 'Success',
            'data': serializer.data
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': {}
        }, status=500)


@csrf_exempt
def ApiSetItemTotalClick(request):
    """
    Increments the total click count for a classified ad.
    """
    try:
        # Fetch the classified ad by ID
        id = request.POST.get('id')
        if not id:
            return JsonResponse({
                'success': False,
                'message': 'ID is required',
                'data': {}
            }, status=400)
        classified_ad = ClassifiedAd.objects.filter(id=id, status='Active').first()
        if not classified_ad:
            return JsonResponse({
                'success': False,
                'message': 'Classified ad not found',
                'data': {}
            }, status=404)

        # Increment the total clicks
        classified_ad.views += 1
        classified_ad.save()

        response = {
            'success': True,
            'message': 'Total click updated successfully',
            'data': {'total_click': classified_ad.views}
        }

        return JsonResponse(response, status=200)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}',
            'data': {}
        }, status=500)