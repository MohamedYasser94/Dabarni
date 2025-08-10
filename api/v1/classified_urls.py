from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1.views import user, common, chat, core
from api.v1.views.apps import front, job, classified


app_name = 'classified'
# DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']
urlpatterns = [

    ##########User API################
    path('auth/signup/register/', user.UserRegister, name="UserRegister"),

    path('auth/login/', user.UserLogin, name="UserLogin"),
    path('auth/logout/', user.UserLogout, name="UserLogout"),
    path('auth/delete-account', user.UserDeleteAccount, name="UserDeleteAccount"),
    path('auth/profile/change-password', user.UserChangePassword, name="UserChangePassword"),

    # path('user/profile', user.UserProfile, name="UserProfile"),
    path('user/module-permission', user.UserModulePermission, name="UserModulePermission"),
    path('profile/update', user.UserProfileUpdate, name="UserProfileUpdate"),
    path('email-verify/', user.VerifyEmail.as_view(), name="email-verify"),
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
    path('search/', common.AdminApiSearch, name='AdminApiSearch'),
    path('currency/', common.ApiCurrencyList, name='ApiCurrencyList'),
    path('language/', common.ApiLanguageList, name='ApiLanguageList'),

    #### chat API ##########
    path('user/chat/pusher/credentials', chat.ApiUserChatPusherCredentials, name='ApiUserChatPusherCredentials'),

    ############### Application API ################

    path('get-system-settings', core.ApiConfigSetting, name='ApiConfigSetting'),
    ### home page #########
    path('slider/', front.ApiHomeSlider, name='ApiHomeSlider'),

    #################### Classified API ##################
    path('classified/categories/', classified.ApiClassifiedCategoryList, name='ApiHomeCategoryList'),
    path('classified/featured-section/', classified.ApiHomeClassifiedFeaturedSection,
         name='ApiHomeClassifiedFeaturedSection'),
    path('classified/get-classified/', classified.ApiHomeClassifiedList, name='ApiHomeClassifiedList'),

    path('classified/get-report-reasons/', classified.ApiGetReportReasons, name='ApiGetReportReasons'),

    path('classified/tips/', classified.ApiGetClassifiedTips, name='ApiGetClassifiedTips'),

    path('classified/get-seller/', classified.ApiGetClassifiedSeller, name='ApiGetClassifiedSeller'),

    path('classified/set-item-total-click/', classified.ApiSetItemTotalClick, name='ApiSetItemTotalClick'),

    # path('classified/top-services/', classified.ApiHomeClassifiedTopServices, name='ApiHomeClassifiedTopServices'),
    # path('classified/top-services-list/', classified.ApiClassifiedTopServicesList, name='ApiClassifiedTopServicesList'),
    # path('classified/recent-jobs/', classified.ApiHomeClassifiedRecentJobs, name='ApiHomeClassifiedRecentJobs'),
    # path('classified/service-details/<int:id>/', classified.ApiClassifiedServiceDetails, name='ApiClassifiedServiceDetails'),



]
