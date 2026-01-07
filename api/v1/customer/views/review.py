from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from apps.classified.models.models import Job, JobReview, JobProgress
from api.v1.customer.serializers.JobReviewCreateSerializer import JobReviewCreateSerializer
from api.v1.response import success_response, error_response
from api.v1.global_serializer.fcm import send_general_notification

@extend_schema(
    tags=["Customer Review"],
    request=JobReviewCreateSerializer,
    responses={201: JobReviewCreateSerializer, 400: 'Error Response', 404: 'Not Found Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createJobReview(request, job_id):
    """
    API endpoint for a customer to submit a rating and review with media for a completed job.
    """
    try:
        job = get_object_or_404(Job, pk=job_id, customer=request.user)
        job_progress = get_object_or_404(JobProgress, job=job)

        if job_progress.progress_status != 'Completed':
            return error_response(
                message="لا يمكن تقييم هذه الوظيفة إلا بعد اكتمالها.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = JobReviewCreateSerializer(data=request.data, context={'request': request, 'job': job})

        if serializer.is_valid():
            review = serializer.save()

            try:
                provider_user = job_progress.provider.user
                customer_name = request.user.get_full_name() or "Client"
                rating_value = getattr(review, 'rating')
                noti_title = "تقييم جديد!"
                noti_body = f"قام {customer_name} بتقييمك بـ {rating_value} نجوم على وظيفة: {job.title}"
                noti_data = {
                    "type": "new_review",
                    "job_id": job.id,
                    "review_id": review.id,
                    "provider_id": job_progress.provider.id,
                    "progress_status": job_progress.progress_status,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }

                send_general_notification(
                    receiver=provider_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="new_review",
                    extra_data=noti_data
                )
            except Exception as noti_error:
                pass

            return success_response(
                message="تم إرسال التقييم بنجاح.",
                data=JobReviewCreateSerializer(review, context={'request': request}).data,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return error_response(
                message="فشل إرسال التقييم.",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )

    except Job.DoesNotExist:
        return error_response(
            message="لم يتم العثور على الوظيفة.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    except JobProgress.DoesNotExist:
        return error_response(
            message="لم يتم العثور على سجل تقدم لهذه الوظيفة. يرجى التواصل مع الدعم.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء إرسال التقييم.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )
    

@extend_schema(
    tags=["Provider Review"],
    request=JobReviewCreateSerializer,
    responses={201: JobReviewCreateSerializer, 400: 'Error Response', 404: 'Not Found Response'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCustomerReview(request, job_id):
    """
    API endpoint for a Provider to submit a rating for a Customer after job completion.
    """
    try:
        job_progress = get_object_or_404(JobProgress, job_id=job_id, provider__user=request.user)
        job = job_progress.job

        if job_progress.progress_status != 'Completed':
            return error_response(
                message="لا يمكن تقييم العميل إلا بعد اكتمال الوظيفة.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = JobReviewCreateSerializer(data=request.data, context={'request': request, 'job': job})

        if serializer.is_valid():
            review = serializer.save()

            try:
                customer_user = job.customer
                provider_name = request.user.get_full_name() or "مقدم خدمة"
                rating_value = getattr(review, 'rating')
                
                noti_title = "تقييم جديد!"
                noti_body = f"قام {provider_name} بتقييم تجربته معك بـ {rating_value} نجوم بخصوص وظيفة: {job.title}"
                
                noti_data = {
                    "type": "new_review_from_provider",
                    "job_id": job.id,
                    "review_id": review.id,
                    "provider_id": job_progress.provider.id,
                    "click_action": "FLUTTER_NOTIFICATION_CLICK"
                }

                send_general_notification(
                    receiver=customer_user,
                    title=noti_title,
                    body=noti_body,
                    notification_type="new_review_from_provider",
                    extra_data=noti_data
                )
            except Exception as noti_error:
                pass

            return success_response(
                message="تم إرسال تقييم العميل بنجاح.",
                data=JobReviewCreateSerializer(review, context={'request': request}).data,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return error_response(
                message="فشل إرسال التقييم.",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )

    except JobProgress.DoesNotExist:
        return error_response(
            message="لم يتم العثور على هذه الوظيفة في سجل أعمالك.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    except Exception as e:
        return error_response(
            message="حدث خطأ أثناء إرسال التقييم.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors={'detail': str(e)}
        )