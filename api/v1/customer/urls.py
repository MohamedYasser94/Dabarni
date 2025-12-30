from django.urls import path, include
from api.v1.customer.views.customer_chat import *
from api.v1.global_views import fcm_notification_views
from apps.front.views import views, blocks 
from api.v1.customer.views import profile ,jop , category, review, customer_wallet
from apps.wallet.views.payment_gateway import paytabs

app_name = 'customer_api'

urlpatterns = [
    path("customer/address/",profile.save_address, name="save-address"),
    path("customer/address/list/",profile.list_addresses, name="list-addresses"),
    path("customer/address/<int:pk>/delete/",profile.delete_address, name="delete-address"),
    path('customer/address/<slug:address_slug>/update/', profile.update_address, name='update-address'),
    #---------------------- Profile --------------
      path("profile/", profile.GetProfileView.as_view(), name="get-profile"),
      path("profile/update/", profile.UpdateProfileView.as_view(), name="update-profile"),
      path("addresses/", profile.list_addresses, name="list-addresses"), 
    # -------------------- Jobs ----------------------------------  
      # Path for creating a new job
    path('jobs/create/', jop.create_job, name='customer-job-create'),
    # Path for listing jobs of the current user
    path('jobs/my/', jop.list_my_jobs, name='customer-jobs-list'),
    # Path for retrieving a single job by ID
    path('jobs/<int:job_id>/', jop.retrieve_job, name='customer-job-retrieve'),
    # Path for listing jobs by progress status
    path('jobs/status/<str:status_param>/', jop.list_jobs_by_progress_status, name='customer-jobs-by-status'),
    path('jobs/<int:job_id>/cancel/', jop.cancel_job, name='customer-job-cancel'),
    path('jobs/progress/<int:progress_id>/approve-extra/', jop.approve_extra_cost, name='customer-approve-extra'),
    path('jobs/progress/<int:progress_id>/reject-extra/', jop.reject_extra_cost, name='customer-reject-extra'),
  #--------------------- Cancel Job with Fee ----------------------------
    path('jobs/<int:job_id>/cancel-with-fee/', jop.CancelJobWithFee, name='customer-cancel-job-with-fee'),
    path('jobs/<int:job_id>/offers/', jop.getOffersByJob, name='customer-job-offers'),
    path('offers/<int:offer_id>/accept/', jop.CustomerAcceptOffer, name='customer-accept-offer'),
    path('jobs/progress/<int:progress_id>/start/', jop.start_Customer_work, name='start_job'),
    path('jobs/progress/<int:progress_id>/finish/', jop.finish_Customer_work, name='providerFinishtJob'),
  #--------------------- Category ----------------------------
      path("categories/", category.list_categories, name="category-list"),
      path("categories/<slug:slug>/", category.retrieve_category, name="category-detail"),
  #--------------------- Review ----------------------------
      path("jobs/<int:job_id>/review/", review.createJobReview, name="create-job-review"),
      #--------------------- Job Negotiate ----------------------------
      path('offers/<int:offer_id>/negotiate/', jop.NegotiateOffer, name='customer-negotiate-offer'),
      path('jobs/<int:job_id>/negotiations/', jop.list_job_negotiations, name='list-job-negotiations'),



    #------------------- Progress ----------------
  path('jobs/progress/<int:progress_id>/', jop.get_job_progress, name='get_job_progress'),

    # ===================== Chat URLs =====================
    path('chat/start/<slug:job_slug>/', customer_start_chat_view, name='start-chat'),
    path('chat/list/', Api_customer_Chat_Lists, name='chat-list'),
    path('chat/messages/', Api_customer_Chat_All_Messages, name='chat-messages'),
    path('chat/messages/save/', customer_send_Messages, name='save-chat-message'),
    path('chat/delete/<uuid:dialog_id>/', customer_delete_specific_chat, name='delete-chat'),

    # ===================== FCM Notification endpoints =====================
    path("fcm-notifications/", include([
        path("", fcm_notification_views.list_notifications, name="customer-fcm-list-notifications"),
        path("create/", fcm_notification_views.create_notification, name="customer-fcm-create-notification"),
        path("<int:notification_id>/", fcm_notification_views.get_notification_detail, name="customer-fcm-notification-detail"),
        path("<int:notification_id>/mark-as-read/", fcm_notification_views.mark_as_read, name="customer-fcm-mark-as-read"),
        path("mark-all-as-read/", fcm_notification_views.mark_all_as_read, name="customer-fcm-mark-all-as-read"),
        path("<int:notification_id>/delete/", fcm_notification_views.delete_notification, name="customer-fcm-delete-notification"),
    ])),

#---------------------- Customer Wallet ---------------------------
     path('wallet/create/', customer_wallet.create_wallet, name='create_wallet'),
    path('wallet/deposit/', customer_wallet.deposit_money, name='deposit_money'),
    path('wallet/withdraw/', customer_wallet.withdraw_money, name='withdraw_money'),
    path('wallet/balance/', customer_wallet.get_balance, name='get_balance'),
    path('wallet/transactions/', customer_wallet.get_transactions, name='get_transactions'),


    ############### Payment Url
    path('payment/paytabs/keys/', paytabs.api_get_paytabs_keys, name='api_get_paytabs_keys'),
    path('callbacks-paytabs/', paytabs.api_callback_url_paytabs, name='api_callback_paytabs'),

    path('user/payment-status-update/', paytabs.ApiJobsPaymentStatusUpdate, name='ApiJobsPaymentStatusUpdate'),
    path('user/payment-status-failed/', paytabs.ApiJobsPaymentStatusFailed, name='ApiJobsPaymentStatusFailed'),

    ################### Job API ##################

    path('callbacks-paytabs/', paytabs.api_callback_url_paytabs, name='api_callback_url_paytabs'),
]
