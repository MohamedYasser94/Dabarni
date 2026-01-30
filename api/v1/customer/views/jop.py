# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\customer\views\jop_request_views.py

from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.utils.crypto import get_random_string
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.shortcuts import get_object_or_404
from api.v1.constants import JobOfferStatus, JobProgressStatus
from api.v1.provider.serializers.classified import JobNegotiateSerializer
from apps.classified.models.models import Coupon, CouponUsage, Job, JobNegotiate, JobOffer, JobProgress
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
from datetime import timedelta
from apps.wallet.models.models import Wallet, WalletMoney, PendingBalanceTransfer
from api.v1.global_serializer.fcm import send_general_notification
from api.v1.utils import get_display_name
from apps.classified.models.models import JobMedia
from api.v1.customer.serializers.media_serializer import JobMediaSerializer

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
            
            # Send notification to all providers in the same category
            try:
                from apps.classified.models.models import JobProvider
                providers_in_category = JobProvider.objects.filter(
                    category=job_instance.category,
                    status='Active'
                ).select_related('user')
                
                customer_name = request.user.get_full_name() or "عميل"
                noti_title = "وظيفة جديدة في تخصصك!"
                noti_body = f"تم نشر وظيفة جديدة: الكمية: {job_instance.quantity}"
                noti_data = {
                    "job_id": job_instance.id,
                    "job_slug": job_instance.slug,
                    "category_id": job_instance.category.id,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
                
                for provider in providers_in_category:
                    try:
                        send_general_notification(
                            receiver=provider.user,
                            title=noti_title,
                            body=noti_body,
                            notification_type="new_job",
                            extra_data=noti_data
                        )
                    except Exception:
                        continue
            except Exception as noti_error:
                pass
            
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
    Excludes offers that have moved to the negotiation stage.
    """
    try:
        negotiations_filter = Prefetch(
            'negotiates',
            queryset=JobNegotiate.objects.all() 
        )

        offers_filter = Prefetch(
            'offers',
            queryset=JobOffer.objects.exclude(status__in=['negotiated', 'Negotiating'])
        )

        jobs = Job.objects.filter(customer=request.user)\
            .select_related('customer', 'category')\
            .prefetch_related(negotiations_filter, offers_filter)

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
        
        # Send notification to provider if assigned
        try:
            if job_progress.provider and job_progress.provider.user:
                provider_user = job_progress.provider.user
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                noti_title = "تم إلغاء الوظيفة"
                noti_body = f"قام {customer_name} بإلغاء الوظيفة. السبب: {reason[:50]}..."
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
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="job_cancelled",
                    extra_data=noti_data
                )
        except Exception as noti_error:
            pass
        
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
    Excludes offers with status 'negotiated'.
    """
    try:
        job = get_object_or_404(Job, pk=job_id, customer=request.user)

        offers = JobOffer.objects.filter(job=job)\
            .exclude(status__in=['negotiated', 'Negotiating'])\
            .select_related('provider__user')

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
        - Send Notification to the Provider
    Returns: job data + progress_id
    """
    try:
        with transaction.atomic():
            offer = get_object_or_404(
                JobOffer.objects.select_related('job__customer', 'provider'),
                pk=offer_id
            )
            job = offer.job
            offer.status = 'Accepted'
            offer.save()
            if job.customer != request.user:
                return error_response(
                    message="ليس لديك صلاحية لقبول هذا العرض.",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            negotiation = JobNegotiate.objects.filter(job=job, provider=offer.provider).first()
            if negotiation and negotiation.customer_accepted:
                return error_response(
                    message="لقد تم قبول تفاوض/عرض سابقاً.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            offer.status = 'Accepted'
            offer.save()

            job_progress = JobProgress.objects.filter(
                job=job,
                customer=job.customer
            ).first()

            if job_progress:
                job_progress.offer = offer
                job_progress.provider = offer.provider
                job_progress.progress_status = 'Pending'
                job_progress.status = 'Pending'
                job_progress.total_cost = offer.price
                job_progress.start_at = None
                job_progress.payment_status = 'Pending'
                job_progress.save()
            else:
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

            if negotiation:
                negotiation.customer_accepted = True
                negotiation.provider_accepted = True
                negotiation.offer = offer
                negotiation.customer_price = offer.price
                negotiation.provider_price = offer.price
                negotiation.save()

            JobOffer.objects.filter(job=job).exclude(pk=offer_id).update(status='Rejected')

            try:
                provider_user = offer.provider.user 
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                noti_title = "تم قبول عرضك!"
                noti_body = f"وافق {customer_name} على عرضك المقدم"
                noti_data = {
                    "job_id": job.id,
                    "job_slug": job.slug,
                    "offer_id": offer.id,
                    "progress_id": job_progress.id,
                    "progress_status": job_progress.progress_status,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }

                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="offer_accepted",
                    extra_data=noti_data
                )
            except Exception as noti_error:
                pass

            other_offers = JobOffer.objects.filter(job=job).exclude(pk=offer_id).select_related('provider__user')
            for other_offer in other_offers:
                try:
                    send_general_notification(
                        receiver=other_offer.provider.user,
                        title="تحديث بخصوص عرضك",
                        body=f"تم إغلاق الوظيفة '{job.title}'. تم اختيار عرض آخر، حظاً أوفر في المرة القادمة!",
                        notification_type="offer_rejected",
                        extra_data={
                            "job_id": job.id,
                            "job_slug": job.slug
                        }
                    )
                except Exception:
                    continue
            other_offers.update(status='Rejected')
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
    summary="بدء العمل الفعلي من العميل",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_Customer_work(request, progress_id):
    try:
        progress = JobProgress.objects.get(id=progress_id)

        if progress.customer != request.user:
            return Response({"status": False, "message": "غير مخول للبدء"}, status=403)

        if progress.start_at:
            return Response({"status": False, "message": "تم بدء العمل مسبقًا"}, status=400)

        if not progress.provider_ready_at:
            return Response({"status": False, "message": "مقدم الخدمة لم يبدأ التجهيز بعد"}, status=400)

        progress.start_at = timezone.now()
        progress.progress_status = "InProgress"
        progress.save()
        
        # Send notification to provider
        try:
            if progress.provider and progress.provider.user:
                provider_user = progress.provider.user
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                noti_title = "بدأ العميل العمل!"
                noti_body = f"بدأ {customer_name} العمل. يمكنك الآن البدء بالتنفيذ."
                noti_data = {
                    "job_id": progress.job.id,
                    "job_slug": progress.job.slug,
                    "progress_id": progress.id,
                    "start_at": str(progress.start_at),
                    "progress_status": progress.progress_status,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
                
                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="work_started",
                    extra_data=noti_data
                )
        except Exception as noti_error:
            pass

        return Response({
            "status": True,
            "message": "تم بدء العمل بنجاح",
            "data": {
                "start_at": progress.start_at,
                "progress_status": progress.progress_status
            }
        })

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)

@extend_schema(
    tags=["Customer Offers"],
    summary="إنهاء العمل واعتماده من قبل العميل",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_Customer_work(request, progress_id):
    try:
        progress = JobProgress.objects.get(id=progress_id)

        if progress.customer != request.user:
            return Response({"status": False, "message": "غير مخول للإنهاء"}, status=403)

        if progress.completed_at or progress.progress_status == "Completed":
            return Response({"status": False, "message": "تم إنهاء العمل واعتماده مسبقًا"}, status=400)

        if not progress.provider_finished_at:
            return Response({"status": False, "message": "لا يمكن إنهاء العمل قبل أن ينهيه مقدم الخدمة"}, status=400)

        now = timezone.now()
        progress.completed_at = now
        progress.end_at = now 
        progress.progress_status = "Completed"
        progress.save()

        try:
            if progress.provider and progress.provider.user:
                provider_user = progress.provider.user
                amount_to_add = progress.total_cost or Decimal('0')
                wallet_money, created = WalletMoney.objects.get_or_create(
                    user=provider_user,
                    defaults={
                        'reversed_balance': amount_to_add,
                    }
                )

                if not created:
                    current_balance = wallet_money.reversed_balance or Decimal('0')
                    wallet_money.reversed_balance = current_balance + amount_to_add
                    wallet_money.save()

                job_content_type = ContentType.objects.get_for_model(Job)
                transfer_date = now + timedelta(days=3)
                PendingBalanceTransfer.objects.create(
                    wallet_money=wallet_money,
                    user=provider_user,
                    amount=amount_to_add,
                    job_content_type=job_content_type,
                    job_id=progress.job.id,
                    transfer_at=transfer_date,
                    status='Pending',
                    notes=f'Auto-created from job completion. Job ID: {progress.job.id}'
                )
        except Exception as e:
            import traceback

        # Send notification to provider
        try:
            if progress.provider and progress.provider.user:
                provider_user = progress.provider.user
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                noti_title = "تم اعتماد إنهاء العمل!"
                noti_body = f"اعتمد {customer_name} إنهاء العمل. تم إكمال الوظيفة بنجاح!"
                noti_data = {
                    "job_id": progress.job.id,
                    "job_slug": progress.job.slug,
                    "progress_id": progress.id,
                    "completed_at": str(progress.completed_at),
                    "progress_status": progress.progress_status,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
                
                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="work_completed",
                    extra_data=noti_data
                )
        except Exception as noti_error:
            pass

        return Response({
            "status": True,
            "message": "تم اعتماد وإنهاء العمل بنجاح",
            "data": {
                "completed_at": progress.completed_at,
                "progress_status": progress.progress_status
            }
        })

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)


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

        if offer.job.customer != request.user:
            return error_response(
                message="ليس لديك صلاحية للتفاوض على هذا العرض.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

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

        negotiation_record, created = JobNegotiate.objects.get_or_create(
            job=offer.job,
            offer=offer,
            provider=offer.provider,
            customer=request.user,
            defaults={
                'customer_price': customer_price,
                'provider_price': offer.price,
                'customer_accepted': True,
                'provider_accepted': None
            }
        )

        if not created:
            negotiation_record.customer_price = customer_price
            negotiation_record.provider_price = offer.price
            negotiation_record.customer_accepted = True
            negotiation_record.provider_accepted = None
            negotiation_record.save()
            message = "تم تحديث عرض التفاوض بنجاح."
        else:
            message = "تم إرسال عرض التفاوض بنجاح."

        offer.status = JobOfferStatus.NEGOTIATING
        offer.save()
        
        # Send notification to provider
        try:
            if offer.provider and offer.provider.user:
                provider_user = offer.provider.user
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                # Try to get job_progress if exists
                job_progress = JobProgress.objects.filter(job=offer.job).first()
                
                noti_title = "عرض تفاوض جديد!"
                noti_body = f"أرسل {customer_name} عرض تفاوض بسعر {customer_price} ريال"
                noti_data = {
                    "job_id": offer.job.id,
                    "job_slug": offer.job.slug,
                    "offer_id": offer.id,
                    "negotiation_id": negotiation_record.id,
                    "customer_price": str(customer_price),
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
                
                # Add progress_status if job_progress exists
                if job_progress:
                    noti_data["progress_id"] = job_progress.id
                    noti_data["progress_status"] = job_progress.progress_status
                
                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="negotiation_offer",
                    extra_data=noti_data
                )
        except Exception as noti_error:
            pass

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

@extend_schema(
    tags=["Customer Offers"],
    request={'action': 'string'},
    responses={200: JobNegotiateSerializer, 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Customer_respond_Negotiation(request, negotiation_id):
    """
    API endpoint for a customer to accept or reject a provider's negotiation offer.
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
            negotiation = get_object_or_404(
                JobNegotiate.objects.select_related('job__customer', 'offer'), 
                pk=negotiation_id
            )

            if negotiation.job.customer != request.user:
                return error_response(
                    message="ليس لديك صلاحية للرد على هذه المفاوضة.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            if negotiation.customer_accepted is not None:
                return error_response(
                    message="تم بالفعل الرد على هذه المفاوضة من قبلك.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if action == 'accept':
                if not negotiation.provider_accepted:
                    return error_response(
                        message="لا يمكن قبول المفاوضة لأن مقدم الخدمة لم يوافق عليها بعد.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                negotiation.customer_accepted = True
                negotiation.save()

                offer = negotiation.offer
                offer.price = negotiation.provider_price 
                offer.status = "negotiated" 
                offer.save()
                job_progress = JobProgress.objects.filter(job=negotiation.job).first()
                if job_progress:
                    job_progress.total_cost = negotiation.provider_price
                    job_progress.save()
                
                message = "تم قبول عرض التفاوض وتحديث سعر العرض بنجاح."
                
                # Send notification to provider on accept
                try:
                    if negotiation.provider and negotiation.provider.user:
                        provider_user = negotiation.provider.user
                        customer_name = get_display_name(request.user.get_full_name(), "العميل")
                        
                        if not job_progress:
                            job_progress = JobProgress.objects.filter(job=negotiation.job).first()
                        
                        noti_title = "تم قبول عرض التفاوض!"
                        noti_body = f"وافق {customer_name} على عرض التفاوض بسعر {negotiation.provider_price} ريال"
                        noti_data = {
                            "job_id": negotiation.job.id,
                            "job_slug": negotiation.job.slug,
                            "offer_id": offer.id,
                            "negotiation_id": negotiation.id,
                            "final_price": str(negotiation.provider_price),
                            "click_action": "FLUTTER_NOTIFICATION_CLICK"
                        }
                        
                        # Add progress_status if job_progress exists
                        if job_progress:
                            noti_data["progress_id"] = job_progress.id
                            noti_data["progress_status"] = job_progress.progress_status
                        
                        send_general_notification(
                            receiver=provider_user,
                            title=noti_title,
                            body=noti_body,
                            notification_type="negotiation_accepted",
                            extra_data=noti_data
                        )
                except Exception as noti_error:
                    pass
            
            elif action == 'reject':
                negotiation.customer_accepted = False 
                negotiation.save()

                offer = negotiation.offer
                offer.status = "negotiated"
                offer.save()
                message = "تم رفض عرض التفاوض بنجاح."
                
                # Send notification to provider on reject
                try:
                    if negotiation.provider and negotiation.provider.user:
                        provider_user = negotiation.provider.user
                        customer_name = get_display_name(request.user.get_full_name(), "العميل")
                        
                        # Try to get job_progress if exists
                        job_progress = JobProgress.objects.filter(job=negotiation.job).first()
                        
                        noti_title = "تم رفض عرض التفاوض"
                        noti_body = f"رفض {customer_name} عرض التفاوض"
                        noti_data = {
                            "job_id": negotiation.job.id,
                            "job_slug": negotiation.job.slug,
                            "offer_id": offer.id,
                            "negotiation_id": negotiation.id,
                            "click_action": "FLUTTER_NOTIFICATION_CLICK"
                        }
                        
                        # Add progress_status if job_progress exists
                        if job_progress:
                            noti_data["progress_id"] = job_progress.id
                            noti_data["progress_status"] = job_progress.progress_status
                        
                        send_general_notification(
                            receiver=provider_user,
                            title=noti_title,
                            body=noti_body,
                            notification_type="negotiation_rejected",
                            extra_data=noti_data
                        )
                except Exception as noti_error:
                    pass

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
        
        # Send notification to provider
        try:
            if progress.provider and progress.provider.user:
                provider_user = progress.provider.user
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                noti_title = "تمت الموافقة على المبلغ الإضافي!"
                noti_body = f"وافق {customer_name} على المبلغ الإضافي {progress.extra_cost} ريال"
                noti_data = {
                    "job_id": progress.job.id,
                    "job_slug": progress.job.slug,
                    "progress_id": progress.id,
                    "progress_status": progress.progress_status,
                    "extra_cost": str(progress.extra_cost),
                    "new_total": str(progress.total_cost),
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
                
                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="extra_cost_approved",
                    extra_data=noti_data
                )
        except Exception as noti_error:
            pass

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


@extend_schema(
    tags=["Customer Jobs"],
    summary="رفض العميل للمبلغ الإضافي",
    description="يقوم العميل برفض التكلفة الإضافية المقترحة من قبل مقدم الخدمة.",
    responses={200: dict, 400: dict, 403: dict, 404: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_extra_cost(request, progress_id):
    """
    العميل يرفض المبلغ الإضافي ويتم تسجيل الرفض
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
                "message": "لا يوجد مبلغ إضافي لرفضه."
            }, status=400)

        if progress.extra_cost_approved is True:
            return Response({
                "status": False,
                "message": "عذراً، لقد قمت بالموافقة على هذا المبلغ مسبقاً ولا يمكن رفضه الآن."
            }, status=400)

        if progress.extra_cost_approved is False:
            return Response({
                "status": False,
                "message": "تم رفض هذا المبلغ مسبقاً."
            }, status=400)

        progress.extra_cost_approved = False
        progress.extra_approved_time = timezone.now() 
        progress.save()
        
        # Send notification to provider
        try:
            if progress.provider and progress.provider.user:
                provider_user = progress.provider.user
                customer_name = get_display_name(request.user.get_full_name(), "العميل")
                
                noti_title = "تم رفض المبلغ الإضافي"
                noti_body = f"رفض {customer_name} المبلغ الإضافي {progress.extra_cost} ريال"
                noti_data = {
                    "job_id": progress.job.id,
                    "job_slug": progress.job.slug,
                    "progress_id": progress.id,
                    "progress_status": progress.progress_status,
                    "extra_cost": str(progress.extra_cost),
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }
                
                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="extra_cost_rejected",
                    extra_data=noti_data
                )
        except Exception as noti_error:
            pass

        return Response({
            "status": True,
            "message": "تم رفض المبلغ الإضافي.",
            "data": {
                "id": progress.id,
                "extra_cost": progress.extra_cost,
                "status": "Rejected"
            }
        }, status=200)

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)
    except Exception as e:
        print(f"Error in reject_extra_cost: {e}")
        return Response({"status": False, "message": "حدث خطأ غير متوقع"}, status=500)

@extend_schema(
    tags=["Coupons"],
    summary="إنشاء كوبون جديد",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "discount_type": {"type": "string", "enum": ["percentage", "fixed"]},
                "discount_value": {"type": "number"},
                "max_usage": {"type": "integer"},
                "max_usage_per_user": {"type": "integer"},
                "valid_to": {"type": "string", "format": "date-time"},
            }
        }
    },
    responses={201: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([AllowAny]) 
def create_coupon(request):
    data = request.data
    discount_value = data.get('discount_value')
    valid_to = data.get('valid_to')
    
    if not all([discount_value, valid_to]):
        return Response({"status": False, "message": "يرجى ملء الحقول الإجبارية (value, valid_to)"}, status=400)

    try:
        new_code = ""
        while True:
            random_str = get_random_string(length=8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            new_code = f"CPN-{random_str}"

            if not Coupon.objects.filter(code=new_code).exists():
                break

        coupon = Coupon.objects.create(
            code=new_code,
            discount_type=data.get('discount_type', 'fixed'),
            discount_value=discount_value,
            max_usage=data.get('max_usage', 100),
            max_usage_per_user=data.get('max_usage_per_user', 1),
            valid_to=valid_to,
            active=True
        )

        return Response({
            "status": True,
            "message": "تم إنشاء الكوبون بنجاح",
            "data": {
                "id": coupon.id,
                "code": coupon.code,
                "discount_value": coupon.discount_value
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"status": False, "message": str(e)}, status=400)


@extend_schema(
    tags=["Coupons"],
    summary="تطبيق كوبون على طلب (مع التحقق من سجل المستخدم)",
    parameters=[
        OpenApiParameter("progress_id", OpenApiTypes.INT, location=OpenApiParameter.PATH),
        OpenApiParameter("code", OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="رمز الكوبون"),
    ],
    responses={200: dict, 400: dict}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_coupon(request, progress_id):
    coupon_code = request.data.get('code') or request.query_params.get('code')
    
    if not coupon_code:
        return Response({"status": False, "message": "يرجى إدخال رمز الكوبون"}, status=400)

    try:
        progress = JobProgress.objects.get(id=progress_id)

        if progress.customer != request.user:
            return Response({"status": False, "message": "غير مصرح لك"}, status=403)

        if progress.coupon:
            return Response({"status": False, "message": "تم استخدام كوبون بالفعل لهذا الطلب"}, status=400)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            return Response({"status": False, "message": "الكوبون غير صحيح"}, status=404)

        if not coupon.is_valid():
            return Response({"status": False, "message": "الكوبون منتهي أو تجاوز الحد الأقصى للاستخدام العام"}, status=400)

        user_usage, created = CouponUsage.objects.get_or_create(user=request.user, coupon=coupon)
        if user_usage.usage_count >= coupon.max_usage_per_user:
            return Response({
                "status": False, 
                "message": f"لقد تجاوزت الحد المسموح لاستخدام هذا الكوبون ({coupon.max_usage_per_user} مرات)"
            }, status=400)

        original_amount = progress.total_cost or Decimal(0)
        if original_amount <= 0:
            return Response({"status": False, "message": "قيمة الطلب غير صالحة للخصم"}, status=400)

        discount_amount = Decimal(0)
        if coupon.discount_type == 'fixed':
            discount_amount = coupon.discount_value
        else:
            discount_amount = (original_amount * coupon.discount_value) / Decimal(100)

        if discount_amount > original_amount:
            discount_amount = original_amount

        with transaction.atomic():
            user_usage.usage_count += 1
            user_usage.save()

            coupon.used_count += 1
            coupon.save()
            progress.coupon = coupon
            progress.coupon_discount_amount = discount_amount
            progress.total_cost = progress.total_cost - progress.coupon_discount_amount
            progress.save()

        return Response({
            "status": True,
            "message": "تم تطبيق الخصم بنجاح",
            "data": {
                "original_total": original_amount,
                "discount_amount": discount_amount,
                "new_total": original_amount - discount_amount,
                "coupon_code": coupon.code
            }
        })

    except JobProgress.DoesNotExist:
        return Response({"status": False, "message": "الطلب غير موجود"}, status=404)
    except Exception as e:
        return Response({"status": False, "message": f"حدث خطأ: {str(e)}"}, status=500)

@extend_schema(
    tags=["Customer Jobs"],
    responses={200: 'Success', 404: 'Not Found Response', 500: 'Error Response'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_confirmation_images(request, job_id):
    """
    API endpoint for customers to view all confirmation images for a specific job.
    Returns images uploaded by the provider with type='confirmation'.
    """
    try:
        job = get_object_or_404(Job, pk=job_id, customer=request.user)
        job_progress = JobProgress.objects.filter(job=job).first()
        
        if not job_progress:
            return error_response(
                message="لم يتم العثور على تقدم العمل لهذا الطلب",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        confirmation_images = JobMedia.objects.filter(
            job_progress=job_progress,
            type='confirmation'
        ).order_by('-created_at')
        
        serializer = JobMediaSerializer(confirmation_images, many=True, context={'request': request})
        
        return success_response(
            message="تم جلب صور التأكيد بنجاح",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            message="حدث خطأ أثناء جلب صور التأكيد",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )