from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.v1.views import user, common, chat, core, wallet, blog
from api.v1.views.apps import front, job, ticket
from apps.wallet.views.payment_gateway import paytabs

app_name = 'job'
urlpatterns = [

    ##########User API################
    path('auth/signup/register/', user.UserRegister, name="UserRegister"),

    path('send-otp-in-mail/', user.SendOtpInMail, name="SendOtpInMail"),

    path('user/send-otp-in-mail/success/', user.SendOtpInMailSuccess, name="SendOtpInMailSuccess"),
    path('auth/login/', user.UserLogin, name="UserLogin"),
    path('auth/logout/', user.UserLogout, name="UserLogout"),
    path('account-delete/', user.UserAccountDelete, name="UserAccountDelete"),
    path('user/change-password/', user.UserChangePassword, name="UserChangePassword"),

    path('user/profile/', user.ApiUserProfile, name="ApiUserProfile"),
    path('user/module-permission', user.UserModulePermission, name="UserModulePermission"),

    # URL for updating the profile
    path('user/update-profile/', user.UserProfileUpdate, name='UserProfileUpdate'),
    path('email-verify/', user.VerifyEmail.as_view(), name="email-verify"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', user.RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', user.PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', user.SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    path('user/singup/check/data/<str:data>/', user.ApiCheckUserDataExist, name='ApiCheckUserDataExist'),
    path('code/<str:coupon>/', user.ApiPromoCodeClient, name='ApiPromoCodeClient'),

    path('auth/signup/otp/', user.ApiUserOtp, name='ApiUserOtp'),
    path('device-token/mobile', user.ApiUserDeviceToken, name='ApiUserDeviceToken'),

    # path('user/address/list', user.ApiUserAddress, name='ApiUserAddress'),
    path('address/list/<str:token>', user.ApiUserAddress, name='ApiUserAddress'),
    path('address/save/', user.ApiUserAddressSave, name='ApiUserAddressSave'),
    path('address/update/<int:id>', user.ApiUserAddressUpdate, name='ApiUserAddressUpdate'),
    path('address/delete/<int:id>', user.ApiUserAddressDelete, name='ApiUserAddressDelete'),
    ##########Search Api################

    path('currency/', common.ApiCurrencyList, name='ApiCurrencyList'),
    path('language/', common.ApiLanguageList, name='ApiLanguageList'),
    path('language-pack/<str:lang_code>/', common.ApiLanguagePack, name='ApiLanguagePack'),

    path('translate-string/', common.ApiTranslateString, name='ApiTranslateString'),
    path('address/governorates/', common.get_saudi_governorates, name='get_saudi_governorates'),
    path('address/cities/<str:governorate_id>/', common.get_saudi_cities, name='get_saudi_cities'),

    #### chat API ##########
    path('user/chat/pusher/credentials', chat.ApiUserChatPusherCredentials, name='ApiUserChatPusherCredentials'),

    ############### Application API ################
path('news/categories/', blog.ApiBlogCategoryList, name='ApiBlogCategoryList'),
    path('news/articles/', blog.ApiBlogArticleList, name='ApiBlogArticleList'),
path('news/articles/<slug:slug>/', blog.ApiBlogArticleDetails, name='ApiBlogArticleDetails'),
path('news/articles/<slug:slug>/viewed/', blog.ApiBlogArticleViewed, name='ApiBlogArticleViewed'),


    path('get-system-settings', core.ApiConfigSetting, name='ApiConfigSetting'),
    ### home page #########
    path('slider/', front.ApiHomeSlider, name='ApiHomeSlider'),

    ################# Jobs API ##################
    path('slider/', front.ApiHomeSlider, name='ApiHomeSlider'),

    path('categories/', job.ApiHomeJobsCategoryList, name='ApiHomeJobsCategoryList'),
    # URL for the main job/service search and filter endpoint
    path('service-list/category-subCategory-rating-sort-by-search/', job.JobSearchView,
         name='job-search-list'),

    # URL to get subcategories based on a parent category ID
    path('category/sub-category/<slug:category_slug>/', job.SubCategoryListView, name='sub-category-list'),
    path('latest-services/', job.ApiHomeJobsLatestServices, name='ApiHomeJobsLatestServices'),
    path('top-services/', job.ApiHomeJobsTopServices, name='ApiHomeJobsTopServices'),
    path('top-services-list/', job.ApiJobsTopServicesList, name='ApiJobsTopServicesList'),
    path('job/recent-jobs/', job.ApiHomeJobsRecentJobs, name='ApiHomeJobsRecentJobs'),
    path('service-details/<slug:slug>/', job.ApiJobsServiceDetails, name='ApiJobsServiceDetails'),

    path('country', job.ApiJobsCountryList, name='ApiJobsCountryList'),

    path('country/service-city/<int:country_id>/', job.ApiJobsServiceCityList, name='ApiJobsServiceCityList'),
    path('user/job/request/request-lists/', job.ApiJobsRequestLists, name='ApiJobsRequestLists'),
    # Category and Sub-category URLs
    path('category/', job.ApiJobsCategoryList, name='ApiJobsCategoryList'),
    path('category/sub-category/<slug:category_slug>/', job.ApiJobsSubCategoryList, name='ApiJobsSubCategoryList'),
    path('category/sub-category/child-category/<slug:sub_category_slug>/', job.ApiJobsChildCategoryList,
         name='ApiJobsChildCategoryList'),

    # Service Search URL
    path('service/search/', job.ApiJobsServiceSearch, name='ApiJobsServiceSearch'),
    path('service/order', job.ApiJobsServiceOrder, name='ApiJobsServiceOrder'),
    path('service/order/<slug:order_slug>', job.ApiJobOrderDetail, name='job_order_detail'),

    ############# User Order API ################
    path('user/my-orders/', job.ApiJobsUserOrderList, name='ApiJobsUserOrderList'),
    path('user/my-orders/<slug:slug>/', job.ApiJobsUserOrderDetail, name='ApiJobsUserOrderDetail'),
    path('user/order/extra-service/list/<slug:slug>/', job.ApiJobsOrderExtraServiceList,
         name='ApiJobsOrderExtraServiceList'),
    path('user/order/request/complete/decline/<slug:slug>/', job.ApiJobsOrderExtraServiceList,
         name='ApiJobsOrderRequestCompleteDecline'),

    path('user/payment-gateway-list/', wallet.ApiJobsPaymentGatewayList, name='ApiJobsPaymentGatewayList'),
    path('payment/paytabs/initiate/', paytabs.api_initiate_paytabs_payment, name='api_initiate_paytabs_payment'),
    path('callbacks-paytabs/', paytabs.api_callback_url_paytabs, name='api_callback_paytabs'),

    ################### Job API ##################
    path('payment-paytabs/<slug:slug>/', paytabs.payment_paytabs, name='PaymentPayTabs'),
    path('callbacks-paytabs/', paytabs.api_callback_url_paytabs, name='api_callback_url_paytabs'),

    ######################### Chat API ########################
    # URL to start a chat with a specific user
    path('start-chat-for-order/<slug:order_slug>/', chat.start_chat_view, name='StartChatForOrder'),
    path('user/chat/all-messages/', chat.ApiUserChatAllMessages, name='ApiUserChatAllMessages'),
    # Add trailing slash handling if needed
    path('user/chat/all-messages/', chat.ApiUserChatAllMessages, name='ApiUserChatAllMessagesNoSlash'),

    # The main chat room URL now accepts a string-based dialog_id
    path('chat/<str:dialog_slug>/', chat.chat_room_view, name='FrontChatRoom'),

    # API endpoint to get the list of active dialogs
    path('api/dialogs/', chat.dialog_list_view, name='FrontApiDialogList'),

    # API endpoint for the Firebase Function to save messages
    path('api/save-chat-message/', chat.SaveChatMessageAPI, name='save-chat-message'),

    path('user/chat/seller-lists/', chat.ApiUserChatSellerLists, name='ApiUserChatSellerLists'),

    #################### Support tiket API #####################
    path('user/support-tickets/', ticket.ApiSupportTicketList, name='ApiSupportTicketList'),
    path('user/view-ticket/<int:id>/', ticket.ApiSupportTicketDetail, name='ApiSupportTicketDetail'),
    path('user/ticket/create/', ticket.ApiSupportTicketCreate, name='ApiSupportTicketCreate'),
    path('user/ticket/message-send/', ticket.ApiSupportTicketMessageSend, name='ApiSupportTicketMessageSend'),



    path('user/add-service-rating/<slug:service_slug>/', ticket.ApiAddServiceRating, name='ApiAddServiceRating'),

    # URL for creating a new report
    path('user/report/create/', ticket.ApiCreateReport, name='ApiCreateReport'),
    path('user/report/list/', ticket.ApiReportList, name='ApiReportList'),
path('user/report/check/<int:order_id>/', ticket.ApiCheckReportExists, name='ApiCheckReportExists'),
    path('user/report/send-message/', ticket.ApiReportMessageSend, name='ApiReportMessageSend'),
    path('user/report/details/<slug:slug>/', ticket.ApiReportDetail, name='ApiReportDetail'),

    # Add this new URL pattern for sending messages


]
