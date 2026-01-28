import math
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.v1.constants import JobProgressStatus
from api.v1.customer.serializers.jop_request_serializer import JobDetailSerializer
from api.v1.provider.serializers.auth import ProviderProfileDetailSerializer, ProviderProfileUpdateSerializer
from api.v1.provider.serializers.review_serializer import ProviderProfileWithReviewsDetailSerializer
from api.v1.provider.serializers.classified import *
from apps.classified.models.models import *
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema ,OpenApiResponse
from apps.classified.models.models import Job
from api.v1.response import success_response, error_response
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Prefetch
from user.models import UserProfile
from api.v1.global_serializer.fcm import send_general_notification
from api.v1.utils import get_display_name

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
    responses={200: ProviderProfileWithReviewsDetailSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def RetrieveProviderProfileById(request, provider_id):
    """
    API endpoint for a customer to get a provider's full profile details by their ID.
    This includes the provider's details, average rating, and a list of their reviews.
    """
    try:
        provider_profile = get_object_or_404(JobProvider, pk=provider_id)
        
        serializer = ProviderProfileWithReviewsDetailSerializer(provider_profile, context={'request': request})
        
        return success_response(
            message="تم جلب ملف مقدم الخدمة بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except JobProvider.DoesNotExist:
        return error_response(
            message="ملف مقدم الخدمة غير موجود.",
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
@api_view(["PATCH"])
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
                data=ProviderProfileDetailSerializer(provider_profile,context={'request': request}).data,
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
    tags=["Provider Orders"],
    responses={200: JobDetailSerializer(many=True), 500: 'Error Response'},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_provider_jobs_by_status(request, status_param):
    """
    API endpoint for Providers to list jobs based on status.
    Filters nested offers/negotiations to show only the provider's own data.
    """
    # valid_statuses = ['Pending', 'Completed', 'Cancelled', 'In Progress', 'Accepted', 'Rejected']
    
    # if status_param not in valid_statuses:
    #     return error_response(
    #         message=f"الحالة غير صالحة. الرجاء استخدام إحدى القيم التالية: {', '.join(valid_statuses)}",
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #     )

    try:
        user = request.user
        my_offers_prefetch = Prefetch(
            'offers', 
            queryset=JobOffer.objects.filter(provider__user=user)
        )
        my_negotiates_prefetch = Prefetch(
            'negotiates', 
            queryset=JobNegotiate.objects.filter(provider__user=user).exclude(provider_accepted=False)
        )

        jobs = Job.objects.filter(
            Q(offers__provider__user=user) | Q(negotiates__provider__user=user)
        ).filter(
            Q(progresses__progress_status__iexact=status_param) |
            Q(offers__status__iexact=status_param, offers__provider__user=user)
        ).prefetch_related(
            my_offers_prefetch,
            my_negotiates_prefetch 
        ).distinct()

        serializer = JobDetailSerializer(jobs, many=True, context={'request': request})
        
        return success_response(
            message=f"تم جلب قائمة وظائف المزود بالحالة '{status_param}' بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message="حدث خطأ أثناء جلب قائمة الوظائف الخاصة بالمزود",
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
    API endpoint to list jobs available for a provider, filtered by their category.
    If coordinates are available (provider's saved location or lat/long query params),
    results are distance-filtered within a given radius (default 50km). Otherwise,
    falls back to category-only results without returning 400.
    Optional query params:
      - lat: float
      - long: float
      - radius_km: float (default 50.0)
    """
    try:
        provider = get_object_or_404(JobProvider, user=request.user)

        # Optional query params override provider location
        qparams = getattr(request, 'query_params', None) or request.GET
        lat_param = qparams.get('lat')
        long_param = qparams.get('long')
        radius_param = qparams.get('radius_km')

        radius_km = 50.0
        try:
            if radius_param is not None:
                radius_km = float(radius_param)
        except Exception:
            radius_km = 50.0

        # Determine coordinates source
        coord_source = None
        providerLat = providerLong = None
        if lat_param and long_param:
            try:
                providerLat = float(lat_param)
                providerLong = float(long_param)
                coord_source = 'query'
            except Exception:
                providerLat = providerLong = None
        if providerLat is None or providerLong is None:
            # fallback to provider saved coords
            try:
                if provider.latitude and provider.longitude:
                    providerLat = float(provider.latitude)
                    providerLong = float(provider.longitude)
                    coord_source = 'provider'
            except Exception:
                providerLat = providerLong = None

        # Base queryset filtered by category and pending progress
        jobsQueryset = (
            Job.objects
            .filter(category=provider.category, progresses__progress_status='Pending')
            .exclude(offers__provider=provider)
            .select_related('location')
            .distinct()
        )

        # If no coordinates available, return category-only results
        if providerLat is None or providerLong is None:
            serializer = JobDetailSerializer(jobsQueryset, many=True, context={'request': request})
            return success_response(
                message="تم جلب قائمة الوظائف المتاحة حسب الفئة. (بدون تحديد موقع)",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        # Distance filtering using Haversine formula in Python
        availableJobs = []
        for job in jobsQueryset:
            if job.location and job.location.latitude and job.location.longitude:
                try:
                    jobLat = float(job.location.latitude)
                    jobLong = float(job.location.longitude)
                except Exception:
                    continue

                R = 6371  # Earth radius in km
                dLat = math.radians(jobLat - providerLat)
                dLon = math.radians(jobLong - providerLong)
                a = math.sin(dLat/2) ** 2 + math.cos(math.radians(providerLat)) * math.cos(math.radians(jobLat)) * math.sin(dLon/2) ** 2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c

                if distance <= radius_km:
                    job.distance = distance
                    availableJobs.append(job)

        availableJobs.sort(key=lambda x: getattr(x, 'distance', float('inf')))
        serializer = JobDetailSerializer(availableJobs, many=True, context={'request': request})

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
        print('Error fetching available jobs:', str(e))
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
        # Corrected line: Pass the request to the serializer context
        serializer = JobDetailSerializer(job, context={'request': request})
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
    tags=["Job Progress"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AcceptJob(request, job_id):
    """
    Provider accepts the job at client's price:
    - creates a JobOffer (or marks existing offer accepted)
    - sets provider_accepted=True and accepted_at
    - Fix: Updates existing JobProgress if found, otherwise creates one.
    - Sends Notification to the Customer.
    """
    try:
        provider = get_object_or_404(JobProvider, user=request.user)
        job = get_object_or_404(Job, pk=job_id)
        existing_offer = JobOffer.objects.filter(job=job, provider=provider).first()

        if existing_offer and existing_offer.provider_accepted:
            return Response({"isSuccess": False, "message": "لقد قمت بقبول هذا الطلب سابقًا."},
                            status=status.HTTP_400_BAD_REQUEST)

        if existing_offer:
            existing_offer.provider_accepted = True
            existing_offer.accepted_at = timezone.now()
            existing_offer.status = 'Pending'
            existing_offer.save()
            offer = existing_offer
        else:
            offer = JobOffer.objects.create(
                job=job,
                provider=provider,
                price=job.price,
                status='InProgress',
            )

        job_progress = JobProgress.objects.filter(job=job).first()

        if job_progress:
            job_progress.provider = provider
            job_progress.offer = offer
            job_progress.progress_status = 'Pending'
            job_progress.status = 'Pending'
            job_progress.total_cost = offer.price
            job_progress.start_at = None
            job_progress.save()
        else:
            job_progress = JobProgress.objects.create(
                job=job,
                provider=provider,
                offer=offer,
                customer=job.customer,
                progress_status='Pending',
                status='Pending',
                total_cost=offer.price,
                start_at=None
            )

        data = JobOfferSerializer(offer, context={'request': request}).data

        try:
            customer_user = job.customer
            provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")

            noti_title = "تم قبول طلبك!"
            noti_body = f"وافق {provider_name} على تنفيذ طلبك بالسعر المحدد."
            noti_data = {
                "type": "job_accepted",
                "job_id": job.id,
                "job_slug": job.slug,
                "progress_id": job_progress.id,
                "progress_status": job_progress.progress_status,
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }

            send_general_notification(
                receiver=customer_user,
                title=noti_title,
                body=noti_body,
                notification_type="job_accepted",
                extra_data=noti_data
            )
        except Exception as noti_error:
            pass

        return Response({"isSuccess": True, "message": "تم قبول الطلب بنجاح", "data": data},
                        status=status.HTTP_201_CREATED)

    except JobProvider.DoesNotExist:
        return Response({"isSuccess": False, "message": "ملف مقدم الخدمة غير موجود."},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"isSuccess": False, "message": "حدث خطأ.", "errors": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    description="Provider marks the job as finished pending customer approval. Optionally upload confirmation images.",
    tags=["Job Progress"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def FinishJob(request, job_id):
    try:
        provider = get_object_or_404(JobProvider, user=request.user)
        job = get_object_or_404(Job, pk=job_id)

        progress = JobProgress.objects.filter(job=job, provider=provider).first()
        if not progress:
            return Response({"status": False, "message": "لا يوجد تقدم مرتبط بهذا الطلب."}, status=status.HTTP_404_NOT_FOUND)

        if progress.provider_finished_at:
            return Response({"status": False, "message": "تم تقديم طلب إنهاء العمل مسبقًا."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            progress.provider_finished_at = timezone.now()
            progress.progress_status = "On Hold to Finish"
            progress.save()
            images = request.FILES.getlist('images')
            uploaded_images = []
            if images:
                for image in images:
                    media = JobMedia.objects.create(
                        job_progress=progress,
                        image=image,
                        type='confirmation'
                    )
                    uploaded_images.append({
                        'id': media.id,
                        'image_url': request.build_absolute_uri(media.image.url) if media.image else None
                    })

            try:
                customer_user = job.customer
                provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
                
                noti_title = "مقدم الخدمة أنهى العمل!"
                noti_body = f"قام {provider_name} بإنهاء العمل. يرجى المراجعة والموافقة لإنهاء الطلب."
                noti_data = {
                    "type": "job_review",
                    "job_id": job.id,
                    "progress_id": progress.id,
                    "progress_status": progress.progress_status,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }

                send_general_notification(
                    receiver=customer_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="job_review",
                    extra_data=noti_data
                )
            except Exception as noti_error:
                pass

        response_data = {
            "progress_status": progress.progress_status,
            "provider_finished_at": progress.provider_finished_at
        }
        
        if uploaded_images:
            response_data["uploaded_images"] = uploaded_images

        return Response({
            "status": True,
            "message": "تم إنهاء العمل من طرفك، بانتظار موافقة العميل.",
            "data": response_data
        }, status=status.HTTP_200_OK)

    except JobProvider.DoesNotExist:
        return Response({"status": False, "message": "ملف مقدم الخدمة غير موجود."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"status": False, "message": "حدث خطأ أثناء إنهاء العمل.", "errors": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["Provider Jobs"],
    request=JobOfferCreateSerializer,
    responses={201: JobOfferSerializer, 400: 'Error Response', 404: 'Not Found Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def SendNewOffer(request):
    """
    API endpoint for a provider to send a new price offer.
    This action creates an offer ONLY.
    """
    try:
        with transaction.atomic():
            provider = get_object_or_404(JobProvider, user=request.user)

            serializer = JobOfferCreateSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                job = serializer.validated_data.get('job')
                price = serializer.validated_data.get('price')
                existingOffer = JobOffer.objects.filter(job=job, provider=provider).first()

                if existingOffer:
                    return error_response(
                        message="لقد قمت بالفعل بتقديم عرض على هذا الطلب. غير مسموح بتقديم أكثر من عرض واحد.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        errors={'detail': 'Duplicate offer not allowed.'}
                    )

                else:
                    offer = JobOffer.objects.create(
                        job=job,
                        provider=provider,
                        price=price,
                        status='Pending'
                    )

                    try:
                        customer_user = job.customer
                        provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
                        noti_title = "عرض سعر جديد!"
                        noti_body = f"قام {provider_name} بتقديم عرض سعر جديد بقيمة {price}"
                        noti_data = {
                            "type": "new_offer",
                            "job_id": job.id,
                            "job_slug": job.slug,
                            "offer_id": offer.id,
                            "click_action": "FLUTTER_NOTIFICATION_CLICK"
                        }
                        
                        # Try to get job_progress to include progress_status if exists
                        job_progress = JobProgress.objects.filter(job=job).first()
                        if job_progress:
                            noti_data["progress_id"] = job_progress.id
                            noti_data["progress_status"] = job_progress.progress_status

                        send_general_notification(
                            receiver=customer_user,
                            title=noti_title,
                            body=noti_body,
                            notification_type="new_offer",
                            extra_data=noti_data
                        )
                    except Exception as noti_error:
                        pass

                return success_response(
                    message="تم تقديم عرضك بنجاح.",
                    data=JobOfferSerializer(offer).data,
                    status_code=status.HTTP_201_CREATED
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

@extend_schema(
    tags=["Provider Negotiations"],
    request={'action': 'string'},
    responses={200: JobNegotiateSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Provider_respond_Negotiation(request, negotiation_id):
    """
    API endpoint for a provider to accept or reject a customer's negotiation offer.
    The request body should contain {'action': 'accept' or 'reject'}.
    """
    action = request.data.get('action')
    if action not in ['accept', 'reject']:
        return error_response(
            message="الإجراء غير صالح. يجب أن يكون 'accept' أو 'reject'.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            negotiation = get_object_or_404(JobNegotiate.objects.select_related('provider__user', 'job', 'offer'), pk=negotiation_id)

            if negotiation.provider.user != request.user:
                return error_response(
                    message="ليس لديك صلاحية للرد على هذه المفاوضة.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            if negotiation.provider_accepted is not None:
                return error_response(
                    message="تم بالفعل الرد على هذه المفاوضة من قبلك.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if action == 'accept':
                if not negotiation.customer_accepted:
                    return error_response(
                        message="لا يمكن قبول المفاوضة لأن العميل لم يوافق عليها بعد.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                negotiation.provider_accepted = True
                negotiation.save()

                offer = negotiation.offer
                offer.price = negotiation.customer_price 
                offer.status = "negotiated" 
                offer.save()
                job_progress = JobProgress.objects.filter(job=negotiation.job).first()
                if job_progress:
                    job_progress.total_cost = negotiation.customer_price
                    job_progress.save()
                
                # Send notification to customer
                try:
                    customer_user = negotiation.job.customer
                    provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
                    
                    noti_title = "وافق مقدم الخدمة على سعرك!"
                    noti_body = f"وافق {provider_name} على سعرك المقترح {negotiation.customer_price} ريال"
                    noti_data = {
                        "job_id": negotiation.job.id,
                        "job_slug": negotiation.job.slug,
                        "negotiation_id": negotiation.id,
                        "offer_id": offer.id,
                        "accepted_price": str(negotiation.customer_price),
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                    
                    # Try to get job_progress to include progress_status if exists
                    if job_progress:
                        noti_data["progress_id"] = job_progress.id
                        noti_data["progress_status"] = job_progress.progress_status
                    
                    send_general_notification(
                        receiver=customer_user,
                        title=noti_title,
                        body=noti_body,
                        notification_type="provider_negotiation_accepted",
                        extra_data=noti_data
                    )
                except Exception as noti_error:
                    pass
                
                message = "تم قبول عرض التفاوض وتحديث سعر العرض بنجاح."
            
            elif action == 'reject':
                negotiation.provider_accepted = False 
                negotiation.save()

                offer = negotiation.offer
                offer.status = "negotiated"
                offer.save()
                
                # Send notification to customer
                try:
                    customer_user = negotiation.job.customer
                    provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
                    
                    noti_title = "رفض مقدم الخدمة سعرك"
                    noti_body = f"رفض {provider_name} سعرك المقترح"
                    noti_data = {
                        "job_id": negotiation.job.id,
                        "job_slug": negotiation.job.slug,
                        "negotiation_id": negotiation.id,
                        "offer_id": offer.id,
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                    
                    # Try to get job_progress to include progress_status if exists
                    job_progress = JobProgress.objects.filter(job=negotiation.job).first()
                    if job_progress:
                        noti_data["progress_id"] = job_progress.id
                        noti_data["progress_status"] = job_progress.progress_status
                    
                    send_general_notification(
                        receiver=customer_user,
                        title=noti_title,
                        body=noti_body,
                        notification_type="provider_negotiation_rejected",
                        extra_data=noti_data
                    )
                except Exception as noti_error:
                    pass
                
                message = "تم رفض عرض التفاوض بنجاح."

        return success_response(
            message=message,
            data=JobNegotiateSerializer(negotiation).data,
            status_code=status.HTTP_200_OK
        )

    except JobNegotiate.DoesNotExist:
        return error_response(
            message="سجل المفاوضة غير موجود.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message=f"حدث خطأ أثناء الرد على المفاوضة: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )


@extend_schema(
    tags=["Provider Negotiations"],
    request=ProviderNegotiateCreateSerializer,
    responses={200: JobNegotiateSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def providerNegotiateResponse(request, negotiation_id):
    """
    API endpoint for a provider to respond to a customer's negotiation offer.
    They can propose a new price, continuing the negotiation.
    """
    try:
        with transaction.atomic():
            negotiation = get_object_or_404(
                JobNegotiate.objects.select_related('provider__user', 'job', 'offer'), 
                pk=negotiation_id
            )

            if negotiation.provider.user != request.user:
                return error_response(
                    message="ليس لديك صلاحية للرد على هذه المفاوضة.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            
            if negotiation.provider_accepted and negotiation.customer_accepted:
                return error_response(
                    message="تم بالفعل الرد على هذه المفاوضة من الطرفين.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ProviderNegotiateCreateSerializer(data=request.data)
            if serializer.is_valid():
                newProviderPrice = serializer.validated_data.get('provider_price')

                negotiation.provider_price = newProviderPrice
                negotiation.provider_accepted = True 
                negotiation.customer_accepted = None

                negotiation.save()
                offer = negotiation.offer
                offer.status = "Negotiating" 
                offer.save()
                
                # Send notification to customer
                try:
                    customer_user = negotiation.job.customer
                    provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
                    
                    noti_title = "عرض سعر مضاد جديد!"
                    noti_body = f"اقترح {provider_name} سعراً جديداً {newProviderPrice} ريال"
                    noti_data = {
                        "job_id": negotiation.job.id,
                        "job_slug": negotiation.job.slug,
                        "negotiation_id": negotiation.id,
                        "offer_id": offer.id,
                        "new_provider_price": str(newProviderPrice),
                        "click_action": "FLUTTER_NOTIFICATION_CLICK"
                    }
                    
                    # Try to get job_progress to include progress_status if exists
                    job_progress = JobProgress.objects.filter(job=negotiation.job).first()
                    if job_progress:
                        noti_data["progress_id"] = job_progress.id
                        noti_data["progress_status"] = job_progress.progress_status
                    
                    send_general_notification(
                        receiver=customer_user,
                        title=noti_title,
                        body=noti_body,
                        notification_type="provider_counter_offer",
                        extra_data=noti_data
                    )
                except Exception as noti_error:
                    pass
                
                return success_response(
                    message="تم إرسال عرض التفاوض بنجاح.",
                    data=JobNegotiateSerializer(negotiation).data,
                    status_code=status.HTTP_200_OK
                )
            else:
                return error_response(
                    message="فشل إرسال عرض التفاوض.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
    except JobNegotiate.DoesNotExist:
        return error_response(
            message="سجل المفاوضة غير موجود.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message=f"حدث خطأ أثناء الرد على المفاوضة: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )


@extend_schema(
    tags=["Provider Jobs"],
    summary="طلب مبلغ إضافي",
    description="المزود يرسل طلب مبلغ إضافي للعميل على عمل جاري",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)   
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_extra_amount(request, progress_id):
    """
    المزود يطلب مبلغ إضافي على عمل جاري
    """
    try:
        progress = JobProgress.objects.get(id=progress_id)

        if not progress.provider or progress.provider.user != request.user:
            return Response({"status": False, "message": "غير مخول لإرسال طلب مبلغ إضافي"}, status=403)

        extra_cost = request.data.get('extra_cost')
        extra_request = request.data.get('extra_request', '')

        if not extra_cost:
            return Response({"status": False, "message": "الرجاء إدخال المبلغ"}, status=400)

        progress.extra_cost = extra_cost
        progress.extra_request = extra_request
        progress.extra_request_time = timezone.now()
        progress.extra_cost_approved = None
        progress.save()
        
        # Send notification to customer
        try:
            customer_user = progress.customer
            provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
            
            noti_title = "طلب مبلغ إضافي"
            noti_body = f"طلب {provider_name} مبلغاً إضافياً {extra_cost} ريال"
            if extra_request:
                noti_body += f". السبب: {extra_request[:50]}"
            
            noti_data = {
                "job_id": progress.job.id,
                "job_slug": progress.job.slug,
                "progress_id": progress.id,
                "progress_status": progress.progress_status,
                "extra_cost": str(extra_cost),
                "extra_request": extra_request,
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }
            
            send_general_notification(
                receiver=customer_user,
                title=noti_title,
                body=noti_body,
                notification_type="extra_amount_requested",
                extra_data=noti_data
            )
        except Exception as noti_error:
            pass

        return Response({
            "status": True,
            "message": f"تم إرسال طلب مبلغ إضافي {extra_cost} بنجاح",
            "data": {
                "extra_cost": progress.extra_cost,
                "extra_request": progress.extra_request,
                "extra_request_time": progress.extra_request_time
            }
        })

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)


@extend_schema(
    tags=["Job Progress"],
    summary="بدء العمل (جاهزية المزود)",
    description="المزود يعلن جاهزيته للبدء، وتتغير الحالة إلى On Hold to Start",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_work(request, progress_id):
    try:
        progress = JobProgress.objects.get(id=progress_id)

        if progress.provider.user != request.user:
            return Response({"status": False, "message": "غير مخول للبدء"}, status=403)

        if progress.provider_ready_at:
            return Response({"status": False, "message": "تم الجاهزية مسبقًا"}, status=400)

        progress.provider_ready_at = timezone.now()
        progress.progress_status = "On Hold to Start"
        progress.save()
        
        # Send notification to customer
        try:
            customer_user = progress.customer
            provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
            
            noti_title = "مقدم الخدمة جاهز للبدء!"
            noti_body = f"أعلن {provider_name} جاهزيته للبدء بالعمل. يمكنك بدء العمل الآن."
            noti_data = {
                "job_id": progress.job.id,
                "job_slug": progress.job.slug,
                "progress_id": progress.id,
                "provider_ready_at": str(progress.provider_ready_at),
                "progress_status": progress.progress_status,
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }
            
            send_general_notification(
                receiver=customer_user,
                title=noti_title,
                body=noti_body,
                notification_type="provider_ready",
                extra_data=noti_data
            )
        except Exception as noti_error:
            pass

        return Response({
            "status": True,
            "message": "تم الجاهزية للعمل، بانتظار بدء العميل",
            "data": {
                "provider_ready_at": progress.provider_ready_at,
                "progress_status": progress.progress_status
            }
        })

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)

@extend_schema(
    tags=["Provider Jobs"], 
    request=None, 
    responses={200: JobDetailSerializer, 400: 'Error Response'}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_job_provider(request, job_id):
    """
    API endpoint for a provider to cancel a job assigned to them.
    """
    reason = request.data.get('reason')
    if not reason:
        return error_response(
            message="الرجاء تقديم سبب للإلغاء.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if hasattr(request.user, 'job_provider_profile'):
            current_provider = request.user.job_provider_profile
        else:
            return error_response(
                message="هذا المستخدم ليس مسجلاً كمقدم خدمة (Provider).",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        job_instance = get_object_or_404(
            Job.objects.prefetch_related('progresses'),
            pk=job_id
        )

        job_progress = job_instance.progresses.filter(provider=current_provider).first()

        if not job_progress:
            return error_response(
                message="أنت غير مكلف بهذه الوظيفة أو لم يتم العثور عليها.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if job_progress.progress_status in ['Completed', 'Cancelled']:
            return error_response(
                message="لا يمكن إلغاء هذه الوظيفة لأنها مكتملة أو ملغية بالفعل.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        job_progress.progress_status = 'Cancelled'
        job_progress.reason = reason
        job_progress.canceled_at = timezone.now()
        job_progress.status = 'InActive'
        job_progress.end_at = timezone.now()
        job_progress.canceled_by = request.user
        job_progress.cancel_provider_approved = True 
        job_progress.save()
        job_instance.status = 'Inactive'
        job_instance.save()
        
        # Send notification to customer
        try:
            customer_user = job_instance.customer
            provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
            
            noti_title = "ألغى مقدم الخدمة الوظيفة"
            noti_body = f"قام {provider_name} بإلغاء الوظيفة. السبب: {reason[:50]}"
            noti_data = {
                "job_id": job_instance.id,
                "job_slug": job_instance.slug,
                "progress_id": job_progress.id,
                "progress_status": job_progress.progress_status,
                "reason": reason,
                "cancelled_at": str(job_progress.canceled_at),
                "click_action": "FLUTTER_NOTIFICATION_CLICK"
            }
            
            send_general_notification(
                receiver=customer_user,
                title=noti_title,
                body=noti_body,
                notification_type="provider_cancelled_job",
                extra_data=noti_data
            )
        except Exception as noti_error:
            pass

        serializer = JobDetailSerializer(job_instance, context={'request': request})
        
        return success_response(
            message="تم إلغاء الوظيفة بنجاح من قبل مقدم الخدمة",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء إلغاء الوظيفة",
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
    
    # Send notification to customer
    try:
        customer_user = job_progress.customer
        provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
        
        noti_title = "طلب مبلغ إضافي"
        noti_body = f"طلب {provider_name} مبلغاً إضافياً {extra_amount} ريال"
        if reason:
            noti_body += f". السبب: {reason[:50]}"
        
        noti_data = {
            "job_id": job_progress.job.id,
            "job_slug": job_progress.job.slug,
            "progress_id": job_progress.id,
            "progress_status": job_progress.progress_status,
            "extra_amount": str(extra_amount),
            "reason": reason,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
        
        send_general_notification(
            receiver=customer_user,
            title=noti_title,
            body=noti_body,
            notification_type="extra_amount_requested",
            extra_data=noti_data
        )
    except Exception as noti_error:
        pass

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
    
    # Send notification to customer
    try:
        customer_user = job_progress.customer
        provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
        
        noti_title = "ألغى مقدم الخدمة الوظيفة"
        noti_body = f"قام {provider_name} بإلغاء الوظيفة"
        noti_data = {
            "job_id": job_progress.job.id,
            "job_slug": job_progress.job.slug,
            "progress_id": job_progress.id,
            "progress_status": job_progress.progress_status,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
        
        send_general_notification(
            receiver=customer_user,
            title=noti_title,
            body=noti_body,
            notification_type="provider_cancelled_job",
            extra_data=noti_data
        )
    except Exception as noti_error:
        pass

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
    
    # Send notification to customer
    try:
        customer_user = job_progress.customer
        provider_name = get_display_name(request.user.get_full_name(), "مقدم خدمة")
        
        noti_title = "أكمل مقدم الخدمة العمل!"
        noti_body = f"أكمل {provider_name} العمل. يرجى المراجعة والاعتماد."
        noti_data = {
            "job_id": job_progress.job.id,
            "job_slug": job_progress.job.slug,
            "progress_id": job_progress.id,
            "progress_status": job_progress.progress_status,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
        
        send_general_notification(
            receiver=customer_user,
            title=noti_title,
            body=noti_body,
            notification_type="provider_completed_work",
            extra_data=noti_data
        )
    except Exception as noti_error:
        pass

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
    try:
        provider = JobProvider.objects.get(user=request.user)
    except JobProvider.DoesNotExist:
        return Response({'message': 'Provider profile not found'}, status=status.HTTP_404_NOT_FOUND)

    job_reviews = JobReview.objects.filter(
        job__progresses__provider=provider
            ).exclude(user=request.user).prefetch_related('media').order_by('-create_at')

    job_reviews_serializer = JobReviewSerializer(job_reviews, many=True, context={'request': request})

    data = {
        "job_reviews": job_reviews_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Provider Jobs"],
    responses={201: 'Success', 404: 'Not Found Response', 400: 'Bad Request', 500: 'Error Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_job_confirmation_images(request, job_id):
    """
    API endpoint for providers to upload confirmation images for a completed job.
    Images are stored in JobMedia with type='confirmation' and linked to JobProgress.
    """
    try:
        provider = get_object_or_404(JobProvider, user=request.user)
        job_progress = JobProgress.objects.filter(
            job_id=job_id,
            provider=provider
        ).first()
        
        if not job_progress:
            return error_response(
                message="لم يتم العثور على تقدم العمل لهذا الطلب",
                status_code=status.HTTP_404_NOT_FOUND
            )

        images = request.FILES.getlist('images')
        if not images:
            return error_response(
                message="يرجى إرفاق صورة واحدة على الأقل",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        created_media = []
        with transaction.atomic():
            for image in images:
                media = JobMedia.objects.create(
                    job_progress=job_progress,
                    image=image,
                    type='confirmation'
                )
                created_media.append(media)

        serializer = JobMediaSerializer(created_media, many=True, context={'request': request})
        return success_response(
            message="تم رفع صور التأكيد بنجاح",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message="حدث خطأ أثناء رفع الصور",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )