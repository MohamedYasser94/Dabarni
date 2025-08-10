import logging

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.v1.serializers.app.job import *
from api.v1.serializers.app.wallet import PurchaseSerializer
from apps.classified.models.job import JobCategories,JobLocation, JobProvider, Job, JobRequirement,JobRequest,JobRequestDocument,JobMedia,JobReview


from rest_framework import serializers, status

from apps.wallet.models.billing import Purchase

User = get_user_model()
logger = logging.getLogger(__name__)


@csrf_exempt
def ApiHomeJobsCategoryList(request):
    """
    This view provides a list of job categories in a format that matches the Flutter application's JobCategory model.
    """
    try:
        category_list = JobCategories.objects.filter(status='Active').order_by('-create_at')
        category_serializer = JobCategoriesSerializer(category_list, many=True, context={'request': request})
        success = True
        message = "Success"
        category_data = category_serializer.data
        data = {'success': success, 'data': category_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)


# View for fetching subcategories
@api_view(['GET'])
@permission_classes([AllowAny])
def SubCategoryListView(request, category_slug):
    """
    Function-based view to get a list of subcategories for a given parent category's slug.
    """
    # Filter subcategories where the parent's slug matches the one from the URL
    queryset = JobCategories.objects.filter(parent__slug=category_slug, status='Active')

    # Serialize the data
    serializer = SubCategorySerializer(queryset, many=True, context={'request': request})

    # Return the response in the desired format
    return Response({'subCategories': serializer.data})


# A custom paginator to match Flutter's expected response structure
class CustomServicePagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number if self.page else 1,
            'data': data,
            'first_page_url': self.get_first_page_url(),
            'from': self.page.start_index() if self.page else 1,
            'last_page': self.page.paginator.num_pages if self.page.paginator else 1,
            'last_page_url': self.get_last_page_url(),
            'links': self.get_links(),
            'next_page_url': self.get_next_link(),
            'path': self.request.path,
            'per_page': self.page_size,
            'prev_page_url': self.get_previous_link(),
            'to': self.page.end_index() if self.page else 0,
            'total': self.page.paginator.count if self.page.paginator else 0,
        })

    def get_first_page_url(self):
        if not self.page:
            return None
        return self.request.build_absolute_uri(self.page.paginator.get_page(1))

    def get_last_page_url(self):
        if not self.page or not self.page.paginator:
            return None
        return self.request.build_absolute_uri(self.page.paginator.get_page(self.page.paginator.num_pages))

    def get_links(self):
        links = []
        if self.page:
            for page_number in range(1, self.page.paginator.num_pages + 1):
                links.append({
                    'url': self.request.build_absolute_uri(self.page.paginator.get_page(page_number)),
                    'label': str(page_number),
                    'active': page_number == self.page.number
                })
        return links


# View for the main service/job search and filter endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def JobSearchView(request):
    """
    Function-based view to search and filter jobs.
    Uses slugs for category and subcategory filtering.
    """
    logger.info("Fetching jobs with function-based view")

    # ======== 1. Get Initial Queryset ========
    queryset = Job.objects.select_related('provider').prefetch_related('job_reviews').filter(status='Active')

    # ======== 2. Get Query Parameters (using slugs) ========
    category_slug = request.query_params.get('cat_slug')
    subcategory_slug = request.query_params.get('subcat_slug')
    rating = request.query_params.get('rating')
    sortby = request.query_params.get('sortby')

    logger.info(
        f"Query params - cat_slug: {category_slug}, subcat_slug: {subcategory_slug}, rating: {rating}, sortby: {sortby}")

    # ======== 3. Apply Filtering ========
    # Handle category and subcategory filtering using slugs
    if subcategory_slug and subcategory_slug != '0':
        queryset = queryset.filter(category__slug=subcategory_slug)
    elif category_slug and category_slug != '0':
        try:
            parent_category = JobCategories.objects.get(slug=category_slug)
            # Get all descendant categories (subcategories) including the parent itself
            all_child_categories = parent_category.get_descendants(include_self=True)
            queryset = queryset.filter(category__in=all_child_categories)
        except JobCategories.DoesNotExist:
            logger.warning(f"Category with slug '{category_slug}' does not exist")
            return Response({'all_services': {'results': []}, 'service_image': []})  # Return empty

    # Handle rating filtering
    if rating and rating.isdigit() and int(rating) > 0:
        queryset = queryset.filter(average_rating__gte=int(rating))

    # ======== 4. Apply Sorting ========
    if sortby:
        if sortby == 'highest_price':
            queryset = queryset.order_by('-cost')
        elif sortby == 'lowest_price':
            queryset = queryset.order_by('cost')
        elif sortby == 'latest_service':
            queryset = queryset.order_by('-create_at')
    else:
        queryset = queryset.order_by('id')  # Default ordering

    logger.info(f"Queryset count: {queryset.count()}")

    # ======== 5. Paginate and Serialize the Results ========
    paginator = CustomServicePagination()
    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer = JobSearchSerializer(page, many=True, context={'request': request})

        # Create the list of service images
        service_images = []
        for job in page:
            first_image = job.image
            if first_image and hasattr(first_image, 'url'):
                service_images.append({'imgUrl': request.build_absolute_uri(first_image.url)})
            else:
                service_images.append(None)

        paginated_response_data = paginator.get_paginated_response(serializer.data).data

        # Structure the final response
        return Response({
            'all_services': paginated_response_data,
            'service_image': service_images
        })

    # This part runs if pagination is not enabled for some reason
    serializer = JobSearchSerializer(queryset, many=True, context={'request': request})
    logger.info("Non-paginated response generated")
    return Response({
        'all_services': {'results': serializer.data},  # Keep structure consistent
        'service_image': []
    })

@csrf_exempt
def ApiHomeJobsLatestServices(request):
    """
    This view provides a list of latest job services in a format that matches the Flutter application's Job model.
    """
    try:
        job_list = Job.objects.filter(status='Active').order_by('-create_at')[:10]
        print('job_list', job_list)
        job_serializer = JobSerializer(job_list, many=True, context={'request': request})
        success = True
        message = "Success"
        job_data = job_serializer.data
        data = {'success': success, 'data': job_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)

@csrf_exempt
def ApiHomeJobsTopServices(request):
    """
    This view provides a list of top job services in a format that matches the Flutter application's Job model.
    """
    try:
        job_list = Job.objects.filter(status='Active').order_by('-views')[:10]
        job_serializer = JobSerializer(job_list, many=True, context={'request': request})
        success = True
        message = "Success"
        job_data = job_serializer.data
        data = {'success': success, 'data': job_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)


@csrf_exempt
def ApiJobsTopServicesList(request):
    """
    This view provides a list of top job services.
    This version is updated to support pagination and returns data in the
    format expected by the TopAllServicesModel in Flutter.
    """
    try:
        all_jobs = Job.objects.filter(status='Active').order_by('-views')

        # Pagination logic based on query parameters from the Flutter app
        page = request.GET.get('page', 1)
        paginate_by = 10  # Default items per page, can be adjusted
        if 'paginate' in request.GET:
            paginate_by = int(request.GET.get('paginate'))

        paginator = Paginator(all_jobs, paginate_by)

        try:
            paginated_jobs = paginator.page(page)
        except PageNotAnInteger:
            paginated_jobs = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            paginated_jobs = paginator.page(paginator.num_pages)

        # Serialize the paginated job data
        job_serializer = JobDetailsSerializer(paginated_jobs, many=True, context={'request': request})

        # The Flutter model also expects 'service_image' and 'reviewer_image'.
        # We will construct these lists based on the paginated jobs.
        service_images = []
        reviewer_images = []

        for job in paginated_jobs:
            # Add service image if it exists
            if job.image and hasattr(job.image, 'url'):
                service_images.append({
                    'image_id': job.id,
                    'path': job.image.name,
                    'img_url': request.build_absolute_uri(job.image.url),
                    'img_alt': None
                })

            # Add reviewer images
            # This assumes a 'profile' object on the user with an 'image' field.
            # This part might need adjustment based on your actual User model structure.
            reviews = JobReview.objects.filter(classified_job=job)
            for review in reviews:
                if hasattr(review.user, 'profile') and hasattr(review.user.profile,
                                                               'image') and review.user.profile.image:
                    reviewer_images.append(request.build_absolute_uri(review.user.profile.image.url))

        # Construct the final paginated response structure to match the Flutter model
        paginated_data = {
            'current_page': paginated_jobs.number,
            'data': job_serializer.data,
            'first_page_url': f"{request.path}?page=1",
            'from': paginated_jobs.start_index(),
            'last_page': paginator.num_pages,
            'last_page_url': f"{request.path}?page={paginator.num_pages}",
            'next_page_url': f"{request.path}?page={paginated_jobs.next_page_number()}" if paginated_jobs.has_next() else None,
            'path': request.build_absolute_uri(request.get_full_path()),
            'per_page': paginator.per_page,
            'prev_page_url': f"{request.path}?page={paginated_jobs.previous_page_number()}" if paginated_jobs.has_previous() else None,
            'to': paginated_jobs.end_index(),
            'total': paginator.count,
        }

        # This is the final data structure that the Flutter model expects
        data = {
            'top_services': paginated_data,
            'service_image': service_images,
            'reviewer_image': reviewer_images,
        }

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500)
@csrf_exempt
def ApiHomeJobsRecentJobs(request):
    """
    This view provides a list of recent job postings in a format that matches the Flutter application's Job model.
    """
    try:
        job_list = Job.objects.filter(status='Active').order_by('-create_at')[:10]
        job_serializer = JobSerializer(job_list, many=True, context={'request': request})
        success = True
        message = "Success"
        job_data = job_serializer.data
        data = {'success': success, 'data': job_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)

@csrf_exempt
def ApiJobsServiceDetails(request,slug):
    """
    This view provides the details of a specific job service.
    It expects a 'slug' parameter to identify the job.
    """
    try:
        job = Job.objects.get(slug=slug, status='Active')
        job_serializer = JobDetailsSerializer(job, context={'request': request})
        success = True
        message = "Success"
        job_data = job_serializer.data
        data = {'success': success, 'data': job_data, 'message': message}
    except Job.DoesNotExist:
        success = False
        message = "Job not found"
        data = {'success': success, 'data': [], 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)


@csrf_exempt
def ApiJobsCountryList(request):
    """
    This view provides a list of countries for job locations.
    """
    try:
        countries = JobLocation.objects.filter(status='Active').order_by('country')
        country_serializer = JobLocationSerializer(countries, many=True, context={'request': request})
        success = True
        message = "Success"
        country_data = country_serializer.data
        data = {'success': success, 'data': country_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)

@csrf_exempt
def ApiJobsServiceCityList(request, country_id):
    """
    This view provides a list of service cities for a given country.
    It expects a 'country_id' parameter to filter the cities.
    """
    try:
        cities = JobLocation.objects.filter(country_id=country_id, status='Active').order_by('city')
        city_serializer = JobLocationSerializer(cities, many=True, context={'request': request})
        success = True
        message = "Success"
        city_data = city_serializer.data
        data = {'success': success, 'data': city_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiJobsRequestLists(request):
    """
    Provides a paginated list of job requests for the authenticated user.
    """
    logger.info(f'Request headers: {request.headers}, method: {request.method}, user: {request.user}')

    try:
        if not request.user.is_authenticated:
            logger.error('User not authenticated')
            return JsonResponse({
                'status': False,
                'detail': 'Authentication credentials were not provided.',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Fetch job requests for the authenticated user
        job_requests_list = JobRequest.objects.filter(user=request.user).order_by('-create_at')

        # Pagination logic
        page = request.GET.get('page', 1)
        paginator = Paginator(job_requests_list, 10)  # 10 requests per page

        try:
            job_requests = paginator.page(page)
        except PageNotAnInteger:
            job_requests = paginator.page(1)
        except EmptyPage:
            return JsonResponse({
                'all_job_request': {
                    'current_page': int(page) if page.isdigit() else 1,
                    'data': [],
                    'last_page': paginator.num_pages,
                    'total': 0
                }
            }, status=status.HTTP_200_OK)

        # Serialize data
        serializer = JobRequestSerializer(job_requests, many=True, context={'request': request})

        # Structure response as expected by Flutter
        response_data = {
            'all_job_request': {
                'current_page': job_requests.number,
                'data': serializer.data,
                'last_page': paginator.num_pages,
                'total': paginator.count,
            }
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f'Error in ApiJobsRequestLists: {str(e)}')
        return JsonResponse({
            'status': False,
            'message': f'Error retrieving job requests: {str(e)}',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiJobsCategoryList(request):
    """
    This view provides a list of top-level job categories.
    The response structure is tailored for the Flutter CategoryApiResponse model.
    """
    try:
        # Fetch only top-level categories (those without a parent)
        categories = JobCategories.objects.filter(status='Active', parent__isnull=True).order_by('title')
        # We assume JobCategoriesSerializer is configured to recursively include children
        serializer = JobCategoriesSerializer(categories, many=True, context={'request': request})

        response_data = {
            'success': True,
            'data': serializer.data,
            'message': "Categories fetched successfully."
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'success': False, 'data': [], 'message': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiJobsSubCategoryList(request, category_id):
    """
    This view provides a list of subcategories for a given category_id.
    The response is structured to be parsed by Flutter's SubcategoryModel.
    """
    try:
        subcategories = JobCategories.objects.filter(parent_id=category_id, status='Active').order_by('title')
        serializer = JobCategoriesSerializer(subcategories, many=True, context={'request': request})

        # The Flutter model expects a `sub_categories` key.
        response_data = {
            'sub_categories': serializer.data
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'sub_categories': []}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiJobsChildCategoryList(request, sub_category_id):
    """
    This view provides a list of child categories for a given sub_category_id.
    The response is structured to be parsed by Flutter's ChildCategoryModel.
    """
    try:
        child_categories = JobCategories.objects.filter(parent_id=sub_category_id, status='Active').order_by('title')
        serializer = JobCategoriesSerializer(child_categories, many=True, context={'request': request})

        # The Flutter model expects a `child_category` key.
        response_data = {
            'child_category': serializer.data,
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'child_category': []}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiJobsServiceSearch(request):
    """
    This view provides a powerful search for jobs based on multiple filters provided
    in the request query parameters, matching the Flutter app's requirements.
    """
    try:
        queryset = Job.objects.filter(status='Active')

        # Text search
        search_text = request.GET.get('search_text')
        if search_text:
            queryset = queryset.filter(Q(title__icontains=search_text) | Q(description__icontains=search_text))

        # Category filters
        child_cat_id = request.GET.get('child_cat')
        if child_cat_id:
            queryset = queryset.filter(category_id=child_cat_id)
        else:
            sub_cat_id = request.GET.get('subcat')
            if sub_cat_id:
                # Filter by subcategory and all its children
                queryset = queryset.filter(
                    category__in=JobCategories.objects.get(id=sub_cat_id).get_descendants(include_self=True))
            else:
                cat_id = request.GET.get('cat')
                if cat_id:
                    # Filter by main category and all its descendants
                    queryset = queryset.filter(
                        category__in=JobCategories.objects.get(id=cat_id).get_descendants(include_self=True))

        # Rating filter
        rating = request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rate__gte=rating)

        # Price range filter
        price_range = request.GET.get('price_range_value')
        if price_range and ',' in price_range:
            min_price, max_price = price_range.split(',')
            if min_price:
                queryset = queryset.filter(cost__gte=min_price)
            if max_price and int(max_price) > 0:
                queryset = queryset.filter(cost__lte=max_price)

        # Note: Geospatial filtering is complex and requires a library like GeoDjango.
        # This is a simplified placeholder for location filtering.
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        if latitude and longitude:
            # Add your logic here to filter by distance if you have lat/long on your JobLocation model
            pass

        # Calculate max price from the filtered queryset
        max_price_value = queryset.aggregate(Max('cost'))['cost__max'] or 0

        # Serialize the final queryset
        serializer = JobDetailsSerializer(queryset, many=True, context={'request': request})

        # Structure the response to match Flutter's ServiceSearchModel
        main_services = []
        for job_data in serializer.data:
            main_services.append({
                "service": job_data,
                "image_url": job_data.get('get_image')  # Assuming serializer provides the image URL
            })

        response_data = {
            "main_services": main_services,
            "max_price": max_price_value,
            "google_map_status": "OK"  # Placeholder value
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            "main_services": [],
            "max_price": 0,
            "message": str(e)
        }, status=500)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def ApiJobsServiceOrder(request):
    """
    Handles the service order request for a job.
    Requires authentication to set the user field.
    Uses the 'cost' field from the Job model for pricing.
    """



    try:
        authenticated_user = request.user
        job_slug = request.data.get('classified_job')

        # Validate inputs
        if not job_slug:
            logger.error("Missing 'classified_job' slug in request")
            return Response({
                'status': False,
                'message': "Missing 'classified_job' slug in request.",
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = Job.objects.get(slug=job_slug)
            # Validate that job has a valid cost
            if not job.cost or float(job.cost) <= 0:
                logger.error(f"Invalid or missing job cost for slug {job_slug}: {job.cost}")
                return Response({
                    'status': False,
                    'message': f"Job with slug {job_slug} has invalid or missing cost.",
                }, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            logger.error(f"Invalid job slug: {job_slug}")
            return Response({
                'status': False,
                'message': f"Invalid job slug: Job with slug {job_slug} does not exist",
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use the job's cost as the price
        price_float = float(job.cost)

        # Create the JobRequest instance
        job_order = JobRequest.objects.create(
            user=authenticated_user,
            classified_job=job,
            price=price_float,
            message=request.data.get('message'),
            negotiable=request.data.get('negotiable', 'No'),
        )

        # Serialize the response with price included
        serializer = JobRequestSerializer(job_order, context={'request': request})
        response_data = serializer.data
        response_data['price'] = str(job_order.price)  # Ensure price is included

        return Response({
            'status': True,
            'message': 'Job order created successfully.',
            'data': response_data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error in ApiJobsServiceOrder: {str(e)}")
        return Response({
            'status': False,
            'message': f'Error creating job order: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiJobOrderDetail(request, order_slug):
    """
    Retrieve details of a specific job order by ID.
    Requires authentication.
    """
    print('ApiJobOrderDetail called with data:', request.data)
    logger.debug(f"Received GET request for job order ID: {order_slug}, Headers: {request.headers}")
    try:
        job_request = JobRequest.objects.get(slug=order_slug, user=request.user)
        purchase = Purchase(
            sender_model=ContentType.objects.get(model='JobRequest'),
            sender_id=job_request.id,
            receiver_model=ContentType.objects.get(model='JobProvider'),
            receiver_id=job_request.classified_job.provider.id,
            owner_model=ContentType.objects.get(model='User'),
            owner_id= request.user.id,
            amount=job_request.final_price,
            source='App',
            purchase_date=timezone.now(),
        )
        purchase.save()
        job_serializer = JobRequestSerializer(job_request, context={'request': request})
        purchase_serializer = PurchaseSerializer(purchase, context={'request': request})
        response_data = job_serializer.data
        response_data['purchase'] = purchase_serializer.data
        response_data['price'] = str(job_request.price)
        return Response({
            'status': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
    except JobRequest.DoesNotExist:
        logger.error(f"Job order with ID {order_slug} not found for user {request.user.id}")
        return Response({
            'status': False,
            'message': f"Job order with ID {order_slug} not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in ApiJobOrderDetail: {str(e)}")
        return Response({
            'status': False,
            'message': f'Error retrieving job order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



############# User Order API ################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiJobsUserOrderList(request):
    """
    Provides a paginated list of job orders for the authenticated user, filtered by payment_status and status.
    """
    logger.info(f'Request headers: {request.headers}, method: {request.method}, user: {request.user}')

    try:
        if not request.user.is_authenticated:
            logger.error('User not authenticated')
            return JsonResponse({
                'status': False,
                'detail': 'Authentication credentials were not provided.',
                'status_code': 403
            }, status=status.HTTP_403_FORBIDDEN)

        # Define status and payment_status options to map indices to values
        order_progress_options = ['Pending', 'Active', 'Complete', 'Delivered', 'Cancelled']
        payment_status_options = ['Pending', 'Complete']

        # Get query parameters from request.data (POST body)
        payment_status_code = request.data.get('payment_status', '')
        progress_code = request.data.get('progress', '')

        # Filter job requests for the authenticated user
        job_requests_list = JobRequest.objects.filter(user=request.user).order_by('-create_at')

        # Apply filters based on payment_status and status codes
        if payment_status_code and payment_status_code.isdigit() and int(payment_status_code) < len(payment_status_options):
            payment_status = payment_status_options[int(payment_status_code)]
            job_requests_list = job_requests_list.filter(payment_status=payment_status)

        if progress_code and progress_code.isdigit() and int(progress_code) < len(order_progress_options):
            status_value = order_progress_options[int(progress_code)]
            job_requests_list = job_requests_list.filter(progress=status_value)

        # Pagination logic
        page = request.data.get('page', 1)
        paginator = Paginator(job_requests_list, 10)  # 10 requests per page

        try:
            job_requests = paginator.page(page)
        except PageNotAnInteger:
            job_requests = paginator.page(1)
        except EmptyPage:
            return JsonResponse({
                'my_orders': {
                    'current_page': int(page) if page.isdigit() else 1,
                    'data': [],
                    'next_page_url': None,
                    'last_page': paginator.num_pages,
                    'total': 0
                },
                'user_id': request.user.id
            }, status=status.HTTP_200_OK)

        # Serialize data
        serializer = JobRequestSerializer(job_requests, many=True, context={'request': request})

        # Construct next_page_url manually to include query parameters
        next_page_url = None
        if job_requests.has_next():
            next_page_url = f"{request.build_absolute_uri('/user/my-orders/')}?page={job_requests.next_page_number()}"
            if payment_status_code:
                next_page_url += f"&payment_status={payment_status_code}"
            if progress_code:
                next_page_url += f"&status={progress_code}"

        # Structure response as expected by Flutter
        response_data = {
            'my_orders': {
                'current_page': job_requests.number,
                'data': serializer.data,
                'next_page_url': next_page_url,
                'last_page': paginator.num_pages,
                'total': paginator.count,
            },
            'user_id': request.user.id
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f'Error in ApiJobsUserOrderList: {str(e)}')
        return JsonResponse({
            'status': False,
            'message': f'Error retrieving job requests: {str(e)}',
            'status_code': 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiJobsUserOrderDetail(request,slug):
    """
    Retrieve details of a specific job order by slug using POST method.
    Requires authentication. The slug should be provided in the request body.
    """
    logger.debug(f"Received POST request for job order, Headers: {request.headers}, Data: {request.data}")
    try:
        # Extract slug from request body

        if not slug:
            logger.error("No slug provided in request body")
            return Response({
                'status': False,
                'message': 'Slug is required in the request body.'
            }, status=status.HTTP_400_BAD_REQUEST)

        job_request = JobRequest.objects.get(slug=slug, user=request.user)

        job_serializer = JobRequestDetailsSerializer(job_request, context={'request': request})
        response_data = job_serializer.data
        response_data['price'] = str(job_request.price)
        return Response({
            'status': True,
            'data': response_data
        }, status=status.HTTP_200_OK)
    except JobRequest.DoesNotExist:
        logger.error(f"Job order with slug {slug} not found for user {request.user.id}")
        return Response({
            'status': False,
            'message': f"Job order with slug {slug} not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in ApiJobsUserOrderDetail: {str(e)}")
        return Response({
            'status': False,
            'message': f'Error retrieving job order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiJobsOrderExtraServiceList(request, slug):
    """
    Retrieve extra services for a specific job order by slug.
    Requires authentication. The slug should be provided in the request body.
    """
    logger.debug(f"Received POST request for extra services, Headers: {request.headers}, Data: {request.data}")
    try:
        # Extract slug from request body
        if not slug:
            logger.error("No slug provided in request body")
            return Response({
                'status': False,
                'message': 'Slug is required in the request body.'
            }, status=status.HTTP_400_BAD_REQUEST)

        job_request = JobRequest.objects.get(slug=slug, user=request.user)
        extra_services = JobRequirement.objects.filter(job_request=job_request)
        extra_service_serializer = JobRequirementSerializer(extra_services, many=True, context={'request': request})

        return Response({
            'status': True,
            'data': extra_service_serializer.data
        }, status=status.HTTP_200_OK)
    except JobRequest.DoesNotExist:
        logger.error(f"Job order with slug {slug} not found for user {request.user.id}")
        return Response({
            'status': False,
            'message': f"Job order with slug {slug} not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in ApiJobsOrderExtraServiceList: {str(e)}")
        return Response({
            'status': False,
            'message': f'Error retrieving extra services: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)