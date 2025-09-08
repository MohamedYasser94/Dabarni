# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\customer\views\jop_request_views.py

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from apps.classified.models.models import Job, JobOffer, JobProgress
from django.db import transaction
from api.v1.customer.serializers.jop_request_serializer import (
    JobCreateSerializer,
    JobDetailSerializer,
    ProviderOfferSerializer,
)
from api.v1.response import success_response, error_response


@extend_schema(
    tags=["Customer Jobs"],
    request=JobCreateSerializer,
    responses={201: JobDetailSerializer, 400: 'Error Response'}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_job(request):
    """
    API endpoint for customers to create a new job.
    """
    serializer = JobCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        try:
            # We no longer pass the user explicitly here, as the serializer handles it
            job_instance = serializer.save()
            response_data = JobDetailSerializer(job_instance).data
            return success_response(
                message="تم نشر الطلب بنجاح",
                data=response_data,
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(
                message="حدث خطأ أثناء إنشاء الطلب",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'detail': str(e)}
            )
    return error_response(
        message="فشل إنشاء الطلب",
        status_code=status.HTTP_400_BAD_REQUEST,
        errors=serializer.errors
    )

@extend_schema(
    tags=["Customer Jobs"],
    responses={200: JobDetailSerializer(many=True), 500: 'Error Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_my_jobs(request):
    """
    API endpoint to list jobs for the current authenticated user.
    """
    try:
        jobs = Job.objects.filter(customer=request.user)
        serializer = JobDetailSerializer(jobs, many=True)
        return success_response(
            message="تم جلب قائمة الوظائف بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب قائمة الوظائف",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )

@extend_schema(
    tags=["Customer Jobs"],
    responses={200: JobDetailSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_job(request, job_id):
    """
    API endpoint to retrieve a single job by its ID.
    """
    try: 
        job = get_object_or_404(Job, pk=job_id)
        serializer = JobDetailSerializer(job)
        return success_response(
            message="تم جلب الوظيفة بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب الوظيفة",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
@extend_schema(
    tags=["Customer Jobs"],
    responses={200: JobDetailSerializer(many=True), 500: 'Error Response'},
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_jobs_by_progress_status(request, status_param):
    """
    API endpoint to list jobs based on their progress status.
    Accepted status values: 'Pending', 'Completed', 'Cancelled'.
    """
    valid_statuses = ['Pending', 'Completed', 'Cancelled','In Progress']
    
    if status_param not in valid_statuses:
        return error_response(
            message=f"الحالة غير صالحة. الرجاء استخدام إحدى القيم التالية: {', '.join(valid_statuses)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        jobs = Job.objects.filter(
            customer=request.user, 
            progresses__progress_status__iexact=status_param
        )

        serializer = JobDetailSerializer(jobs, many=True)
        return success_response(
            message=f"تم جلب قائمة الوظائف بالحالة '{status_param}' بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب قائمة الوظائف",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )


@extend_schema(
    tags=["Customer Jobs"],
    # request={'reason': 'text'}, # Use a simple dictionary for the request body
    responses={200: JobDetailSerializer, 400: 'Error Response'}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_job(request, job_id):
    """
    API endpoint for a customer to cancel a job.
    """
    reason = request.data.get('reason')
    if not reason:
        return error_response(
            message="الرجاء تقديم سبب للإلغاء.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        
        job_instance = get_object_or_404(
            Job.objects.prefetch_related('progresses'),
            pk=job_id,
            customer=request.user
        )

        job_progress = job_instance.progresses.first()

        if not job_progress:
            return error_response(
                message="لم يتم العثور على تقدم لهذا الطلب.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if job_progress.progress_status in ['Completed', 'Cancelled']:
            return error_response(
                message="لا يمكن إلغاء هذه الوظيفة لأنها مكتملة أو ملغية بالفعل.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Update the JobProgress record with cancellation details
        job_progress.progress_status = 'Cancelled'
        job_progress.reason = reason
        job_progress.canceled_at = timezone.now()
        job_progress.status='InActive'
        job_progress.end_at=timezone.now()
        job_progress.canceled_by = request.user
        job_progress.save()

        # Update the main Job's status field as well for consistency
        job_instance.status = 'Inactive'
        job_instance.save()

        return success_response(
            message="تم إلغاء الوظيفة بنجاح",
            data=JobDetailSerializer(job_instance).data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء إلغاء الوظيفة",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
@extend_schema(
    tags=["Customer Jobs"],
    responses={200: ProviderOfferSerializer(many=True), 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOffersByJob(request, job_id):
    """
    API endpoint for a customer to view all offers for a specific job.
    """
    try:
        # Get the job, ensuring it belongs to the authenticated user
        job = get_object_or_404(Job, pk=job_id, customer=request.user)

        # Corrected line: Use select_related to get the provider and its user in one query
        offers = JobOffer.objects.filter(job=job).select_related('provider__user')

        # Serialize the offers
        serializer = ProviderOfferSerializer(offers, many=True)

        return success_response(
            message="تم جلب العروض بنجاح.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Job.DoesNotExist:
        return error_response(
            message="لم يتم العثور على الطلب.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب العروض.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )

@extend_schema(
    tags=["Customer Jobs"],
    responses={200: JobDetailSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customerAcceptOffer(request, offer_id):
    """
    API endpoint for a customer to accept a specific job offer.
    """
    try:
        # Get the offer, ensuring it belongs to the authenticated customer's job
        offer = get_object_or_404(JobOffer.objects.select_related('job__customer'), pk=offer_id)

        # Check if the offer's job is owned by the current user
        if offer.job.customer != request.user:
            return error_response(
                message="ليس لديك صلاحية لقبول هذا العرض.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if offer.status in ['Accepted', 'Rejected']:
            return error_response(
                message="لا يمكن قبول هذا العرض. لقد تم قبوله أو رفضه بالفعل.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # 1. Update the accepted offer
            offer.customer_accepted = True
            offer.status = 'Accepted'
            offer.save()
            
            # 2. Update the main Job record
            job = offer.job
            job.status = 'Assigned' # Job is now assigned
            job.save()

            # 3. Update the JobProgress record to link the accepted offer
            job_progress, created = JobProgress.objects.get_or_create(job=job)
            job_progress.offer = offer
            job_progress.provider = offer.provider
            job_progress.progress_status = 'Assigned' # Progress is now assigned
            job_progress.total_cost = offer.price # Set the total cost to the accepted price
            job_progress.save()

            # 4. Reject all other offers for this job
            JobOffer.objects.filter(job=job).exclude(pk=offer_id).update(status='Rejected')

        return success_response(
            message="تم قبول العرض بنجاح. لقد تم تعيين مقدم الخدمة.",
            data=JobDetailSerializer(job).data,
            status_code=status.HTTP_200_OK
        )
    except JobOffer.DoesNotExist:
        return error_response(
            message="العرض غير موجود.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء قبول العرض.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )