# api/v1/global_views/fcm_notification_views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter
from api.v1.response import success_response, error_response
from api.v1.global_serializer.common_serializer import FcmNotificationSerializer
from apps.classified.models.ticket import FcmNotification
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["FCM Notifications"],
    parameters=[
        OpenApiParameter(
            name='is_read',
            description='Filter by read status (true/false)',
            required=False,
            type=bool
        )
    ]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def list_notifications(request):
    """
    Get all notifications for the authenticated user.
    Optional: Filter by is_read status
    """
    try:
        user = request.user
        # Only return notifications for the current user
        notifications = FcmNotification.objects.filter(user=user)

        # Optional filter by is_read status
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            notifications = notifications.filter(is_read=is_read)

        serializer = FcmNotificationSerializer(notifications, many=True)

        return success_response(
            message="Notifications retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        print('Error fetching notifications',e)
        return error_response(
            message="Error fetching notifications",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=str(e)
        )


@extend_schema(
    tags=["FCM Notifications"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_notification_detail(request, notification_id):
    """
    Get a specific notification and mark it as read
    """
    try:
        user = request.user
        notification = FcmNotification.objects.get(id=notification_id, user=user)

        # Mark as read
        if not notification.is_read:
            notification.is_read = True
            notification.save()

        serializer = FcmNotificationSerializer(notification)

        return success_response(
            message="Notification retrieved and marked as read",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except FcmNotification.DoesNotExist:
        return error_response(
            message="Notification not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error retrieving notification: {str(e)}")
        return error_response(
            message="Error retrieving notification",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=str(e)
        )


@extend_schema(
    tags=["FCM Notifications"],
    request=FcmNotificationSerializer
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def create_notification(request):
    """
    Create a new notification for the authenticated user.
    Only superusers/admins can create notifications for other users.
    """
    try:
        user = request.user
        data = request.data.copy()

        # Determine target user: default to current user
        target_user = user
        provided_user_id = data.get('user')
        if provided_user_id and user.is_superuser:
            # Superusers may create notifications for other users
            target_user = provided_user_id  # pass id; serializer.save(user_id) expects instance or id depending on serializer

        # Remove user from payload to avoid conflicting assignment
        if 'user' in data:
            data.pop('user')

        serializer = FcmNotificationSerializer(data=data)

        if serializer.is_valid():
            # Explicitly assign the user
            serializer.save(user=target_user)

            return success_response(
                message="Notification created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return error_response(
                message="Validation error",
                status_code=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return error_response(
            message="Error creating notification",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=str(e)
        )


@extend_schema(
    tags=["FCM Notifications"],
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def delete_notification(request, notification_id):
    """
    Delete a specific notification
    """
    try:
        user = request.user
        notification = FcmNotification.objects.get(id=notification_id, user=user)
        notification.delete()

        return success_response(
            message="Notification deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT
        )
    except FcmNotification.DoesNotExist:
        return error_response(
            message="Notification not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        return error_response(
            message="Error deleting notification",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=str(e)
        )


@extend_schema(
    tags=["FCM Notifications"],
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def mark_as_read(request, notification_id):
    """
    Mark a notification as read
    """
    try:
        user = request.user
        notification = FcmNotification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save()

        serializer = FcmNotificationSerializer(notification)

        return success_response(
            message="Notification marked as read",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    except FcmNotification.DoesNotExist:
        return error_response(
            message="Notification not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return error_response(
            message="Error marking notification as read",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=str(e)
        )


@extend_schema(
    tags=["FCM Notifications"],
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def mark_all_as_read(request):
    """
    Mark all notifications as read for the authenticated user
    """
    try:
        user = request.user
        unread_count = FcmNotification.objects.filter(user=user, is_read=False).update(is_read=True)

        return success_response(
            message=f"All {unread_count} unread notification(s) marked as read",
            data={"updated_count": unread_count},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return error_response(
            message="Error marking notifications as read",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            errors=str(e)
        )
