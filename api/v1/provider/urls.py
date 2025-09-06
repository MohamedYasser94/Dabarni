from django.urls import path
from api.v1.provider.views import provider_auth, provider_home, provider_wallet, provider_chat
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
     path('profile/update/', provider_home.updateProviderProfile, name='provider-profile-update'),
      #---------------------------------------------------------------------------
    path("home/", provider_home.ProviderHome, name="ProviderHome"),
    path('jobs/available/', provider_home.RetrieveAvailableJobs, name='provider-available-jobs'),
    path('jobs/<int:job_id>/details/', provider_home.GetJobDetails, name='provider-job-details'),
    path('jobs/make-request/', provider_home.SendNewOffer, name='providerSendOffer'),
    path('jobs/<int:job_id>/accept/', provider_home.AcceptJob, name='providerAcceptJob'),
    path("profile/", ProviderProfile, name="ProviderProfile"),
    path("profile/update/", ProviderUpdateProfile, name="ProviderUpdateProfile"),
    path("profile/reviews/", provider_home.ProviderJobReviews, name="ProviderJobReviews"),
    path("profile/update-fcm-token/", provider_auth.update_fcm_token, name="update_fcm_token"),

    # ===================== Job & Order URLs =====================
    path("orders/<str:progress_status>/", provider_home.ProviderMyOrders, name="ProviderMyOrders"),
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

    # ===================== Wallet & Payout URLs =====================
    path("wallet/", provider_wallet.ProviderWallet, name="ProviderWallet"),
    path("wallet/payouts/", provider_wallet.ProviderPayoutRequestList, name="ProviderPayoutRequestList"),
    path("wallet/payouts/request/", provider_wallet.ProviderPayoutRequest, name="ProviderPayoutRequest"),
    path("wallet/payouts/<int:payout_id>/", provider_wallet.ProviderPayoutRequestDetail, name="ProviderPayoutRequestDetail"),
    path("wallet/payment-gateways/", provider_wallet.PaymentGatewayList, name="PaymentGatewayList"),
    path("wallet/bank-account/", provider_wallet.ProviderBankAccount, name="ProviderBankAccount"),
    path("wallet/bank-account/add/", provider_wallet.AddProviderBankAccount, name="AddProviderBankAccount"),

    # ===================== Chat URLs =====================
    path("chat/start/<slug:order_slug>/", provider_chat.StartChatView, name="StartChatView"),
    path("chat/dialogs/", provider_chat.ApiUserChatSellerLists, name="ApiUserChatSellerLists"),
    path("chat/messages/", provider_chat.ApiProviderChatMessages, name="ApiProviderChatMessages"),
    path("chat/messages/save/", provider_chat.SaveChatMessageAPI, name="SaveChatMessageAPI"),
]
