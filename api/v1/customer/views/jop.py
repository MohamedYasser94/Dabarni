# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\customer\views\jop_request_views.py

from django.utils import timezone
from flask import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from api.v1.constants import JobOfferStatus, JobProgressStatus
from apps.classified.models.models import Job, JobNegotiate, JobOffer, JobProgress
from django.db import transaction
from django.db.models import Prefetch
from api.v1.customer.serializers.jop_request_serializer import (
    JobCreateSerializer,
    JobDetailSerializer,
    JobNegotiateCreateSerializer,
    JobNegotiateListSerializer,
    ProviderOfferSerializer,
)
from api.v1.response import success_response, error_response
from apps.wallet.models.models import Wallet


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
            job_instance = serializer.save()
            # هنا أضفنا الـ context
            response_data = JobDetailSerializer(job_instance, context={'request': request}).data
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
    Shows negotiations ONLY if both customer_price and provider_price are set.
    """
    try:
        negotiations_filter = Prefetch(
            'negotiates',
            queryset=JobNegotiate.objects.filter(
                customer_price__isnull=False, 
                provider_price__isnull=False
            )
        )

        jobs = Job.objects.filter(customer=request.user)\
            .select_related('customer', 'category')\
            .prefetch_related(negotiations_filter) 
        serializer = JobDetailSerializer(jobs, many=True, context={'request': request})
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
        serializer = JobDetailSerializer(job, context={"request": request})
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
    Accepted status values: 'Pending', 'Completed', 'Cancelled', 'In Progress', 'Assigned'.
    """
    valid_statuses = ['Pending', 'Completed', 'Cancelled','In Progress','Assigned']
    
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

        serializer = JobDetailSerializer(jobs, many=True, context={'request': request})
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
        serializer = JobDetailSerializer(job_instance, context={'request': request})
        return success_response(
            message="تم إلغاء الوظيفة بنجاح",
            data=serializer.data,
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
    request={'reason': 'text'},
    responses={200: JobDetailSerializer, 400: 'Error Response', 404: 'Not Found Response'}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def CancelJobWithFee(request, job_id):
    """
    API endpoint for a customer to cancel a job with a cancellation fee.
    """
    reason = request.data.get('reason')
    if not reason:
        return error_response(
            message="الرجاء تقديم سبب للإلغاء.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            # Get the Job and its related progress record
            job_instance = get_object_or_404(Job, pk=job_id, customer=request.user)
            job_progress = get_object_or_404(JobProgress, job=job_instance)

            # Check if the job is already completed or canceled
            if job_progress.progress_status in ['Completed', 'Cancelled']:
                return error_response(
                    message="لا يمكن إلغاء هذه الوظيفة لأنها مكتملة أو ملغية بالفعل.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            
            # Define the cancellation fee based on your business rules
            cancellationFee = 10.00
            
            # Get the customer's wallet and check the balance
            try:
                wallet = get_object_or_404(Wallet, user=request.user)
            except Wallet.DoesNotExist:
                return error_response(
                    message="محفظة العميل غير موجودة.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if wallet.amount < cancellationFee:
                return error_response(
                    message="رصيدك غير كافٍ لإلغاء الطلب.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            # Deduct the fee from the customer's wallet
            wallet.amount -= cancellationFee
            wallet.save()

            # Update the JobProgress record with cancellation details
            job_progress.progress_status = 'Cancelled'
            job_progress.reason = reason
            job_progress.canceled_at = timezone.now()
            job_progress.canceled_by = request.user
            job_progress.cancel_cost = cancellationFee
            job_progress.end_at = timezone.now()
            job_progress.save()

            # Update the main Job's status
            job_instance.status = 'Canceled'
            job_instance.save()
            
            # Return success response with the updated job details
            return success_response(
                message=f"تم إلغاء الطلب بنجاح. تم خصم {cancellationFee} ريال.",
                data=JobDetailSerializer(job_instance).data,
                status_code=status.HTTP_200_OK
            )
            
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء إلغاء الطلب",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
    
@extend_schema(
    tags=["Customer Offers"],
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
        serializer = ProviderOfferSerializer(offers, many=True, context={'request': request})
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
def CustomerAcceptOffer(request, offer_id):
    """
    Accept an offer (API).
    This endpoint will:
        - mark the offer as Accepted
        - create/update the JobProgress and set it to InProgress
        - mark other offers as Rejected
    Returns: job data + progress_id
    """
    try:
        with transaction.atomic():
            offer = get_object_or_404(
                JobOffer.objects.select_related('job__customer', 'provider'),
                pk=offer_id
            )
            job = offer.job

            # تأكيد صلاحية العميل
            if job.customer != request.user:
                return error_response(
                    message="ليس لديك صلاحية لقبول هذا العرض.",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            # راجع الـ negotiation إن وجد
            negotiation = JobNegotiate.objects.filter(job=job, provider=offer.provider).first()
            if negotiation and negotiation.customer_accepted:
                return error_response(
                    message="لقد تم قبول تفاوض/عرض سابقاً.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Update offer
            offer.status = 'Accepted'
            offer.save()

            # ابحث عن JobProgress للـ job + customer
            job_progress = JobProgress.objects.filter(
                job=job,
                customer=job.customer
            ).first()

            if job_progress:
                # لو موجود → نعدله
                job_progress.offer = offer
                job_progress.provider = offer.provider
                job_progress.progress_status = 'Pending'
                job_progress.status = 'Pending'
                job_progress.total_cost = offer.price
                job_progress.start_at = None
                job_progress.payment_status = 'Pending'
                job_progress.save()
            else:
                # لو مش موجود → نكريت جديد
                job_progress = JobProgress.objects.create(
                    job=job,
                    offer=offer,
                    provider=offer.provider,
                    customer=job.customer,
                    progress_status='Pending',
                    status='Pending',
                    total_cost=offer.price,
                    start_at=None,
                    payment_status='Pending'
                )

            # Update negotiation if present
            if negotiation:
                negotiation.customer_accepted = True
                negotiation.provider_accepted = True
                negotiation.offer = offer
                negotiation.customer_price = offer.price
                negotiation.provider_price = offer.price
                negotiation.save()

            # Reject other offers
            JobOffer.objects.filter(job=job).exclude(pk=offer_id).update(status='Rejected')

        # prepare response data (include progress_id so frontend can redirect)
        job_data = JobDetailSerializer(job, context={"request": request}).data
        response_data = {
            "job": job_data,
            "progress_id": job_progress.id
        }
        return success_response(
            message="تم قبول العرض بنجاح. لقد تم تعيين مقدم الخدمة.",
            data=response_data,
            status_code=status.HTTP_200_OK
        )

    except JobOffer.DoesNotExist:
        return error_response(
            message="العرض غير موجود.",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء قبول العرض.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )


@extend_schema(
    tags=["Customer Offers"],
    request=JobNegotiateCreateSerializer,
    responses={200: JobNegotiateCreateSerializer, 400: 'Bad Request', 403: 'Forbidden', 404: 'Not Found', 500: 'Error'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def NegotiateOffer(request, offer_id):
    """
    API endpoint for a customer to negotiate on a provider's offer.
    If a negotiation record exists it will be UPDATED with the new customer price.
    If not exists it will be CREATED.
    """
    try:
        offer = get_object_or_404(JobOffer.objects.select_related('job__customer', 'provider'), pk=offer_id)

        # only job owner (customer) can negotiate
        if offer.job.customer != request.user:
            return error_response(
                message="ليس لديك صلاحية للتفاوض على هذا العرض.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # can't negotiate on accepted/rejected offers
        if str(offer.status).lower() in ['accepted', 'rejected']:
            return error_response(
                message="لا يمكن التفاوض على هذا العرض. لقد تم قبوله أو رفضه بالفعل.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = JobNegotiateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="فشل إرسال عرض التفاوض.",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )

        customer_price = serializer.validated_data.get('customer_price')

        # حاول الحصول على السجل أو إنشاؤه — لكن لا ترفض لو موجود: قم بالتحديث بدلاً من ذلك
        negotiation_record, created = JobNegotiate.objects.get_or_create(
            job=offer.job,
            offer=offer,
            provider=offer.provider,
            customer=request.user,
            defaults={
                'customer_price': customer_price,
                # ممكن تملأ حقول افتراضية أخرى هنا لو تحتاج
            }
        )

        if not created:
            # حدث التفاوض الموجود: حدّث السعر وارجع حالة القبول للمزود لـ False لأن السعر تغيّر
            negotiation_record.customer_price = customer_price
            negotiation_record.provider_accepted = False
            negotiation_record.customer_accepted = False
            negotiation_record.save()
            message = "تم تحديث عرض التفاوض بنجاح."
        else:
            message = "تم إرسال عرض التفاوض بنجاح."

        # تأكد أن حالة الـ offer تشير إلى التفاوض
        offer.status = JobOfferStatus.NEGOTIATING
        offer.save()

        return success_response(
            message=message,
            data=JobNegotiateCreateSerializer(negotiation_record).data,
            status_code=status.HTTP_200_OK
        )

    except JobOffer.DoesNotExist:
        return error_response(
            message="العرض غير موجود.",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء التفاوض.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_job_progress(request, progress_id):
    try:
        progress = JobProgress.objects.get(id=progress_id, start_at__isnull=False)

        return success_response(
            message="حالة الطلب",
            data={
                "status": progress.progress_status,
                "start_at": progress.start_at,
                "total_cost": progress.total_cost,
            }
        )
    except JobProgress.DoesNotExist:
        return error_response(
            message="لم يتم العثور على التقدم الذي بدأ بعد.",
            status_code=status.HTTP_404_NOT_FOUND
        )

@extend_schema(
    tags=["Customer Offers"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_job_negotiations(request, job_id):
    try:
        job = get_object_or_404(Job, pk=job_id)

        if job.customer != request.user:
            return error_response(
                message="ليس لديك صلاحية لعرض مفاوضات هذا العمل.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        negotiations = JobNegotiate.objects.filter(job=job).select_related('offer', 'provider')
        serializer = JobNegotiateListSerializer(negotiations, many=True, context={'request': request})

        return success_response(
            message="تم جلب قائمة المفاوضات بنجاح.",
            data={
                "negotiations": serializer.data
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء جلب المفاوضات.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )    
    

@extend_schema(
    tags=["Customer Jobs"],
    summary="موافقة العميل على المبلغ الإضافي",
    description="يقوم العميل بالموافقة على التكلفة الإضافية، ويتم تحديث السعر الكلي للطلب تلقائياً.",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_extra_cost(request, progress_id):
    """
    العميل يوافق على المبلغ الإضافي ويتم إضافته للمجموع الكلي
    """
    try:
        progress = JobProgress.objects.get(id=progress_id)

        if progress.customer != request.user:
            return Response({
                "status": False,
                "message": "عذراً، هذا الطلب لا يخصك."
            }, status=403)

        if not progress.extra_cost or progress.extra_cost <= 0:
            return Response({
                "status": False,
                "message": "لا يوجد مبلغ إضافي مطلوب للموافقة عليه."
            }, status=400)

        if progress.extra_cost_approved:
            return Response({
                "status": False,
                "message": "تمت الموافقة على هذا المبلغ مسبقاً."
            }, status=400)

        progress.extra_cost_approved = True
        progress.extra_approved_time = timezone.now()
        current_total = progress.total_cost if progress.total_cost else 0
        new_total = current_total + progress.extra_cost
        progress.total_cost = new_total
        progress.save()

        return Response({
            "status": True,
            "message": "تمت الموافقة على المبلغ الإضافي بنجاح.",
            "data": {
                "id": progress.id,
                "extra_cost": progress.extra_cost,
                "new_total_cost": progress.total_cost,
                "approved_at": progress.extra_approved_time
            }
        }, status=200)

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)
    except Exception as e:
        print(f"Error in approve_extra_cost: {e}")
        return Response({"status": False, "message": "حدث خطأ غير متوقع"}, status=500)