from django.urls import path, include
from api.v1 import authentication
from api.v1.global_views import fcm_notification_views

app_name = 'app_api'

urlpatterns = [

    path("auth/register/", authentication.register, name="register"),
    path("auth/verify-otp/", authentication.verify_otp, name="verify-otp"),
    path("logout/", authentication.logout, name="logout"),

    # FCM Notification endpoints - using include for better organization
    path("notifications/", include([
        path("", fcm_notification_views.list_notifications, name="list-notifications"),
        path("create/", fcm_notification_views.create_notification, name="create-notification"),
        path("<int:notification_id>/", fcm_notification_views.get_notification_detail, name="notification-detail"),
        path("<int:notification_id>/mark-as-read/", fcm_notification_views.mark_as_read, name="mark-as-read"),
        path("mark-all-as-read/", fcm_notification_views.mark_all_as_read, name="mark-all-as-read"),
        path("<int:notification_id>/delete/", fcm_notification_views.delete_notification, name="delete-notification"),
    ])),

]
