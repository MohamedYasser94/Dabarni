from django.urls import path

from api.v1.customer.views import review
from api.v1.global_views import fcm_notification_views
from api.v1.provider.views import provider_auth, provider_home, provider_wallet
from api.v1.provider.views.notification_views import NotificationDeleteView, NotificationListView
from api.v1.provider.views.providerchat import *
from api.v1.provider.views.provider_home import ProviderProfile, ProviderUpdateProfile

app_name = 'provider_api'

urlpatterns = [
    # ===================== Authentication URLs =====================
    path("auth/register/", provider_auth.ProviderRegister, name="ProviderRegister"),
    path("auth/verify-otp/", provider_auth.verify_signup_otp, name="verify_signup_otp"),
    path("auth/login/", provider_auth.UserLogin, name="UserLogin"),
    path("auth/logout/", provider_auth.UserLogout, name="UserLogout"),
    path("auth/change-password/", provider_auth.UserChangePassword, name="UserChangePassword"),
    path("auth/delete-account/", provider_auth.UserAccountDelete, name="UserAccountDelete"),
    path("auth/password-reset/request/", provider_auth.RequestPasswordResetSMS.as_view(), name="request_password_reset"),
    path("auth/password-reset/verify-otp/", provider_auth.verify_reset_otp, name="verify_reset_otp"),
    path("auth/password-reset/by-phone/", provider_auth.reset_password_by_phone, name="reset_password_by_phone"),

    # ===================== Profile & Home URLs =====================
    path('profile/complete-info/', provider_auth.completeProviderProfile, name='provider-profile-complete-info'),
    path('profile/', provider_home.retrieveProviderProfile, name='provider-profile-detail'),
    path('profile/<int:provider_id>/', provider_home.RetrieveProviderProfileById, name='providerProfileByIdWithReviews'),
    path('profile/update/', provider_home.updateProviderProfile, name='provider-profile-update'),
    #------------------------------- Provider Home Jobs --------------------------------------------
    path("home/", provider_home.ProviderHome, name="ProviderHome"),
    path('jobs/available/', provider_home.RetrieveAvailableJobs, name='provider-available-jobs'),
    path('jobs/<int:job_id>/details/', provider_home.GetJobDetails, name='provider-job-details'),
    path('jobs/make-request/', provider_home.SendNewOffer, name='providerSendOffer'),
    path('jobs/negotiate-offer/<int:negotiation_id>/', provider_home.Provider_respond_Negotiation, name='provider-negotiate-offer'),
    path('negotiations/<int:negotiation_id>/respond/', provider_home.providerNegotiateResponse, name='provider-negotiate-response'),
    path('jobs/<int:job_id>/accept/', provider_home.AcceptJob, name='providerAcceptJob'),
    path('jobs/<int:job_id>/finish/', provider_home.FinishJob, name='providerFinishtJob'),
    path("profile/", ProviderProfile, name="ProviderProfile"),
    path("profile/update/", ProviderUpdateProfile, name="ProviderUpdateProfile"),
    path("profile/reviews/", provider_home.ProviderJobReviews, name="ProviderJobReviews"),
    path("profile/update-fcm-token/", provider_auth.update_fcm_token, name="update_fcm_token"),

    # ===================== Job & Order URLs =====================
    path("orders/<str:progress_status>/", provider_home.ProviderMyOrders, name="ProviderMyOrders"),
    path('jobs/status/<str:status_param>/', provider_home.list_provider_jobs_by_status, name='list-provider-jobs-by-status'),
    # path("jobs/<slug:job_slug>/details/", provider_home.ProviderJobDetails, name="ProviderJobDetails"),
    path("jobs/offers/<slug:offer_slug>/details/", provider_home.ProviderJobOfferDetails, name="ProviderJobOfferDetails"),
    path("jobs/offers/<slug:offer_slug>/update-status/", provider_home.ProviderUpdateJobOfferStatus, name="ProviderUpdateJobOfferStatus"),
    path("jobs/progress/<slug:progress_slug>/details/", provider_home.ProviderJobProgressDetails, name="ProviderJobProgressDetails"),
    path("jobs/progress/<slug:progress_slug>/update-status/", provider_home.ProviderUpdateJobProgressStatus, name="ProviderUpdateJobProgressStatus"),
    path("jobs/progress/<slug:progress_slug>/negotiations/", provider_home.ProviderJobNegotiations, name="ProviderJobNegotiations"),
    path("jobs/progress/<slug:progress_slug>/request-extra-money/", provider_home.jobRequestExtraMoney, name="jobRequestExtraMoney"),
    path("jobs/progress/<slug:progress_slug>/cancel/", provider_home.ProviderJobCancelRequest, name="ProviderJobCancelRequest"),
    path("jobs/progress/<slug:progress_slug>/complete/", provider_home.ProviderJobCompleteRequest, name="ProviderJobCompleteRequest"),
    path("jobs/negotiations/<int:negotiation_id>/update-status/", provider_home.ProviderUpdateJobNegotiationStatus, name="ProviderUpdateJobNegotiationStatus"),

    path('jobs/progress/<int:progress_id>/extra-request/', provider_home.request_extra_amount, name='request_extra_amount'),
    path('jobs/progress/<int:progress_id>/start/', provider_home.start_work, name='start_job'),
    # ===================== Wallet & Payout URLs =====================
    path("wallet/", provider_wallet.ProviderWallet, name="ProviderWallet"),
    path("wallet/payouts/", provider_wallet.ProviderPayoutRequestList, name="ProviderPayoutRequestList"),
    path("wallet/payouts/request/", provider_wallet.ProviderPayoutRequest, name="ProviderPayoutRequest"),
    path("wallet/payouts/<int:payout_id>/", provider_wallet.ProviderPayoutRequestDetail, name="ProviderPayoutRequestDetail"),
    path("wallet/payment-gateways/", provider_wallet.PaymentGatewayList, name="PaymentGatewayList"),
    path("wallet/bank-account/", provider_wallet.ProviderBankAccount, name="ProviderBankAccount"),
    path("wallet/bank-account/add/", provider_wallet.AddProviderBankAccount, name="AddProviderBankAccount"),

    # ===================== Chat URLs =====================
    path('chat/start/<slug:job_slug>/', provider_start_chat_view, name='start-chat'),
    path('chat/list/', Api_provider_Chat_Lists, name='chat-list'),
    path('chat/messages/', Api_provider_Chat_All_Messages, name='chat-messages'),
    path('chat/messages/save/', provider_send_Messages, name='save-chat-message'),
    path('chat/delete/<uuid:dialog_id>/', provider_delete_specific_chat, name='delete-chat'),

        #--------------------- Review ----------------------------
    path("jobs/<int:job_id>/review-customer/", review.createCustomerReview, name="create-customer-review"),

    # ===================== Notification URLs =====================
    path('notifications/', NotificationListView.as_view(), name='provider-notification-list'),
    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification-delete'),

# FCM Notification endpoints
    path("notifications/", fcm_notification_views.list_notifications, name="list-notifications"),
    path("notifications/create/", fcm_notification_views.create_notification, name="create-notification"),
    path("notifications/<int:notification_id>/", fcm_notification_views.get_notification_detail, name="notification-detail"),
    path("notifications/<int:notification_id>/mark-as-read/", fcm_notification_views.mark_as_read, name="mark-as-read"),
    path("notifications/mark-all-as-read/", fcm_notification_views.mark_all_as_read, name="mark-all-as-read"),
    path("notifications/<int:notification_id>/delete/", fcm_notification_views.delete_notification, name="delete-notification"),
]
