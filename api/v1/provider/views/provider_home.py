import math
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.v1.customer.serializers.jop_request_serializer import JobDetailSerializer
from api.v1.provider.serializers.auth import ProviderProfileDetailSerializer, ProviderProfileUpdateSerializer
from api.v1.provider.serializers.classified import *
from apps.classified.models.models import *
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Q
from apps.classified.models.models import Job
from api.v1.response import success_response, error_response
from api.v1.customer.serializers.profile_serializer import UserProfileSerializer
from django.db.models.expressions import RawSQL

@extend_schema(
    tags=["Provider Profile"],
    responses={200: ProviderProfileDetailSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieveProviderProfile(request):
    """
    API endpoint to get the authenticated provider's full profile details.
    """
    try:
        provider_profile = get_object_or_404(JobProvider, user=request.user)
        
        serializer = ProviderProfileDetailSerializer(provider_profile, context={'request': request})
        
        return success_response(
            message="تم جلب ملف مقدم الخدمة بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى إتمام التسجيل أولاً.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الملف",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
@extend_schema(
    tags=["Provider Profile"],
    request=ProviderProfileUpdateSerializer,
    responses={200: ProviderProfileDetailSerializer, 400: 'Error Response'}
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateProviderProfile(request):
    """
    API endpoint to update a provider's profile.
    Accepts partial data and saves it across multiple models.
    """
    user = request.user
    
    try:
        provider_profile = JobProvider.objects.get(user=user)
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى إتمام التسجيل أولاً.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProviderProfileUpdateSerializer(
        provider_profile,
        data=request.data,
        partial=True,
        context={'request': request}
    )

    if serializer.is_valid():
        try:
            provider_profile = serializer.save()
            return success_response(
                message="تم تحديث ملف مقدم الخدمة بنجاح",
                data=ProviderProfileDetailSerializer(provider_profile).data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(
                message="حدث خطأ أثناء تحديث الملف",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'detail': str(e)}
            )
    else:
        return error_response(
            message="فشل تحديث ملف مقدم الخدمة",
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderHome(request):
    provider = JobProvider.objects.get(id=request.user.id)
    job_progress = JobProgress.objects.filter(provider=provider)
    job_offer = JobOffer.objects.filter(provider=provider)

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, many=True,context={'request': request})
    job_offer_serializer = JobOfferSerializer(job_offer, many=True,context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)
@extend_schema(
    tags=["Provider Orders"],
    responses={200: 'ProviderOrdersResponse', 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderMyOrders(request, progress_status):
    """
    API endpoint to retrieve a provider's orders based on a specific progress status.
    This includes jobs they have offers on or are actively working on.
    """
    try:
        provider = get_object_or_404(JobProvider, user=request.user)
        
        jobProgress = JobProgress.objects.filter(provider=provider, progress_status=progress_status)
        jobOffer = JobOffer.objects.filter(provider=provider, status=progress_status)

        jobProgressSerializer = JobProgressSerializer(jobProgress, many=True, context={'request': request})
        jobOfferSerializer = JobOfferSerializer(jobOffer, many=True, context={'request': request})

        data = {
            "jobProgress": jobProgressSerializer.data,
            "jobOffer": jobOfferSerializer.data,
        }
        
        return success_response(
            message="تم جلب الطلبات بنجاح.",
            data=data,
            status_code=status.HTTP_200_OK
        )
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى التأكد من أنك سجلت كمقدم خدمة.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الطلبات.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )



@extend_schema(
    tags=["Provider Jobs"],
    responses={200: JobDetailSerializer(many=True), 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def RetrieveAvailableJobs(request):
    """
    API endpoint to list jobs available for a provider, filtered by their category
    and geographical location using Python-based calculation.
    """
    try:
        # 1. Get the authenticated provider's profile and their location
        provider = get_object_or_404(JobProvider, user=request.user)

        if not provider.latitude or not provider.longitude:
            return error_response(
                message="يرجى إكمال ملفك الشخصي وإضافة موقعك لتتمكن من رؤية الوظائف المتاحة.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        providerLat = float(provider.latitude)
        providerLong = float(provider.longitude)
        searchRadiusKm = 50.0  # 50 kilometers radius

        # 2. Get jobs filtered by category and prefetch the related UserAddress data
        jobsQueryset = Job.objects.filter(
            category=provider.category,
            progresses__progress_status='Pending'
        ).select_related('location')

        # 3. Calculate distance for each job and filter in Python
        availableJobs = []
        for job in jobsQueryset:
            if job.location and job.location.latitude and job.location.longitude:
                jobLat = float(job.location.latitude)
                jobLong = float(job.location.longitude)
                
                # Haversine formula calculation in Python
                R = 6371 # Earth radius in km
                dLat = math.radians(jobLat - providerLat)
                dLon = math.radians(jobLong - providerLong)
                a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(providerLat)) * math.cos(math.radians(jobLat)) * math.sin(dLon/2) * math.sin(dLon/2)
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c

                if distance <= searchRadiusKm:
                    # Add a distance attribute to the job object for sorting later
                    job.distance = distance
                    availableJobs.append(job)

        # Sort the list of jobs by distance
        availableJobs.sort(key=lambda x: x.distance)

        # 4. Serialize the filtered jobs
        serializer = JobDetailSerializer(availableJobs, many=True)
        
        return success_response(
            message="تم جلب قائمة الوظائف المتاحة لك بنجاح.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى إكمال ملفك الشخصي.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(
            message=f"حدث خطأ أثناء جلب قائمة الوظائف: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
    
@extend_schema(
    tags=["Provider Jobs"],
    responses={200: JobDetailSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def GetJobDetails(request, job_id):
    """
    API endpoint for a provider to get the full details of a specific job.
    """
    try:
        job = get_object_or_404(Job, pk=job_id)
        serializer = JobDetailSerializer(job)
        return success_response(
            message="تم جلب تفاصيل الطلب بنجاح.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب تفاصيل الطلب.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )

@extend_schema(
    tags=["Provider Jobs"],
    responses={200: JobDetailSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AcceptJob(request, job_id):
    """
    API endpoint for a provider to immediately accept a job at the client's price.
    """
    try:
        provider = get_object_or_404(JobProvider, user=request.user)
        job = get_object_or_404(Job, pk=job_id)
        
        # Check if an offer already exists from this provider for this job
        existingOffer = JobOffer.objects.filter(job=job, provider=provider).first()

        if existingOffer:
            return error_response(
                message="لقد قمت بتقديم عرض على هذا الطلب بالفعل. يمكنك تعديل عرضك.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            
        # Create a new offer with the job's original price
        offer = JobOffer.objects.create(
            job=job,
            provider=provider,
            price=job.price,
            provider_accepted=True,
            status='InProgress',
        )

        return success_response(
            message="تم قبول الطلب بنجاح. سيتم إخطار العميل.",
            data=JobOfferSerializer(offer).data,
            status_code=status.HTTP_201_CREATED
        )
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى إكمال ملفك الشخصي.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء قبول الطلب.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
        
@extend_schema(
    tags=["Provider Jobs"],
    request=JobOfferCreateSerializer,
    responses={201: JobOfferCreateSerializer, 400: 'Error Response', 404: 'Not Found Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def SendNewOffer(request):
    """
    API endpoint for a provider to send a new price offer or update an existing one.
    """
    try:
        provider = get_object_or_404(JobProvider, user=request.user)

        serializer = JobOfferCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            jobId = serializer.validated_data.get('job').id
            price = serializer.validated_data.get('price')

            existingOffer = JobOffer.objects.filter(job_id=jobId, provider=provider).first()

            if existingOffer:
                existingOffer.price = price
                existingOffer.status = 'New'
                existingOffer.save()
                offer = existingOffer
                message = "تم تحديث عرضك بنجاح."
                status_code = status.HTTP_200_OK
            else:
                offer = serializer.save(provider=provider)
                message = "تم تقديم عرضك بنجاح."
                status_code = status.HTTP_201_CREATED

            return success_response(
                message=message,
                data=JobOfferSerializer(offer).data,
                status_code=status_code
            )
        else:
            return error_response(
                message="فشل تقديم عرضك.",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
            
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود. يرجى إكمال ملفك الشخصي.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء تقديم العرض.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )

#============================================= last edits ============================================= 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobOfferDetails(request,offer_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_offer = JobOffer.objects.get(slug=offer_slug,provider=provider)
    except JobOffer.DoesNotExist:
        return Response({"error": "Job offer not found or you do not have permission to view this job offer."}, status=status.HTTP_404_NOT_FOUND)

    ### serializers
    job_offer_serializer = JobOfferSerializer(job_offer, context={'request': request})

    data = {
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobNegotiations(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to view this job progress."}, status=status.HTTP_404_NOT_FOUND)

    negotiations = JobNegotiate.objects.filter(job=job_progress.job,provider=provider)

    ### serializers
    negotiations_serializer = JobNegotiateSerializer(negotiations, many=True,context={'request': request})

    data = {
        "negotiations": negotiations_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateJobNegotiationStatus(request,negotiation_id):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_negotiation = JobNegotiate.objects.get(id=negotiation_id,provider=provider)
    except JobNegotiate.DoesNotExist:
        return Response({"error": "Job negotiation not found or you do not have permission to update this job negotiation."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'accepted', 'rejected']:
        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    job_negotiation.status = new_status
    job_negotiation.save()

    ### serializers
    job_negotiation_serializer = JobNegotiateSerializer(job_negotiation, context={'request': request})

    data = {
        "job_negotiation": job_negotiation_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobProgressDetails(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to view this job progress."}, status=status.HTTP_404_NOT_FOUND)

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateJobOfferStatus(request,offer_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_offer = JobOffer.objects.get(slug=offer_slug,provider=provider)
    except JobOffer.DoesNotExist:
        return Response({"error": "Job offer not found or you do not have permission to update this job offer."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'accepted', 'rejected', 'cancelled']:
        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    job_offer.status = new_status
    job_offer.save()

    ### serializers
    job_offer_serializer = JobOfferSerializer(job_offer, context={'request': request})

    data = {
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateJobProgressStatus(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    job_progress.status = new_status
    job_progress.save()

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jobRequestExtraMoney(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    extra_amount = request.data.get('extra_amount')
    reason = request.data.get('reason','')

    if not extra_amount or float(extra_amount) <= 0:
        return Response({"error": "Invalid extra amount."}, status=status.HTTP_400_BAD_REQUEST)

    job_negotiation = JobNegotiate.objects.create(
        job=job_progress.job,
        provider=provider,
        amount=extra_amount,
        reason=reason,
        status='pending'
    )

    ### serializers
    job_negotiation_serializer = JobNegotiateSerializer(job_negotiation, context={'request': request})

    data = {
        "job_negotiation": job_negotiation_serializer.data,
    }
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderJobCancelRequest(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    if job_progress.status == 'cancelled':
        return Response({"error": "Job progress is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

    job_progress.status = 'cancelled'
    job_progress.save()

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderJobCompleteRequest(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    if job_progress.status == 'completed':
        return Response({"error": "Job progress is already completed."}, status=status.HTTP_400_BAD_REQUEST)

    job_progress.status = 'completed'
    job_progress.save()

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderProfile(request):
    provider = JobProvider.objects.get(id=request.user.id)

    ### serializers
    provider_serializer = JobProviderSerializer(provider, context={'request': request})

    data = {
        "provider": provider_serializer.data,
        "profile_completion_percentage": provider.profile_completion_percentage
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateProfile(request):
    try:
        # Get all related objects for the authenticated user
        user = request.user
        provider = user.job_provider_profile
        profile = user.profile
    except JobProvider.DoesNotExist:
        return Response({"error": "Provider profile not found."}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    # --- 1. Update User Model Fields ---
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.save()

    # --- 2. Update UserProfile Model Fields ---
    profile.dob = data.get('dob', profile.dob)
    profile.nationality = data.get('nationality', profile.nationality)
    profile.residence = data.get('residence', profile.residence)
    profile.id_number = data.get('id_number', profile.id_number)
    if 'id_image_front' in request.FILES:
        profile.id_image_front = request.FILES['id_image_front']
    if 'id_image_back' in request.FILES:
        profile.id_image_back = request.FILES['id_image_back']
    if 'residence_image' in request.FILES:
        profile.residence_image = request.FILES['residence_image']
    profile.save()

    # --- 3. Update JobProvider Model Fields ---
    provider.experience_years = data.get('experience_years', provider.experience_years)
    provider.company = data.get('company', provider.company)
    provider.bio = data.get('bio', provider.bio)
    provider.website = data.get('website', provider.website)
    provider.business_phone = data.get('business_phone', provider.business_phone)
    provider.address = data.get('address', provider.address)
    provider.commercial_number = data.get('commercial_number', provider.commercial_number)
    provider.vat_number = data.get('vat_number', provider.vat_number)
    provider.license_number = data.get('license_number', provider.license_number)
    provider.bank_account = data.get('bank_account', provider.bank_account)
    if 'commercial_image' in request.FILES:
        provider.commercial_image = request.FILES['commercial_image']
    if 'commercial_image2' in request.FILES:
        provider.commercial_image2 = request.FILES['commercial_image2']
    if 'vat_image' in request.FILES:
        provider.vat_image = request.FILES['vat_image']
    if 'license_image' in request.FILES:
        provider.license_image = request.FILES['license_image']

    # The save method will automatically recalculate the completion percentage
    provider.save()

    # Serialize the updated provider data
    provider_serializer = JobProviderSerializer(provider, context={'request': request})

    # Prepare the final response
    response_data = {
        "provider": provider_serializer.data,
        "profile_completion_percentage": provider.data_progress  # Use the saved field
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobReviews(request):
    provider = JobProvider.objects.get(id=request.user.id)
    job_reviews = JobReview.objects.filter(provider=provider)

    ### serializers
    job_reviews_serializer = JobReviewSerializer(job_reviews, many=True,context={'request': request})

    data = {
        "job_reviews": job_reviews_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)