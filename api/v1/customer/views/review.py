# D:\Python Projects\Dabarni_fork\Dabarni\api\v1\customer\views\jop_request_views.py

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
                data=JobReviewCreateSerializer(review).data,
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