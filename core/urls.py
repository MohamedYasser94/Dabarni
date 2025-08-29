from django.urls import path
from core.views import localization, notifications, users, \
    utilities, core

app_name = 'core'

urlpatterns = [

    path('', core.AdminIndex, name='AdminIndex'),
    path('login/', users.AdminLogin.as_view(), name='AdminLogin'),
    path('lockscreen', users.AdminLockscreen.as_view(), name='AdminLockscreen'),
    path('logout/', users.AdminLogout, name='AdminLogout'),
    path('notifications/', notifications.AdminNotificationslist, name='AdminNotificationsList'),
    path('notifications/<slug:slug>/', notifications.AdminNotificationsDetails, name='AdminNotificationsDetails'),
    path('403/', core.AdminError403, name='AdminError403'),
    path('404/', core.AdminError404, name='AdminError404'),


    ########## Blog Admin #########




    ########## Users Admin #########
    path('user/', users.AdminUsersList, name='AdminUserList'),
    path('user/detail/<slug:slug>/', users.AdminUserDetail, name='AdminDetailUser'),
    path('user/address/<slug:slug>/', users.AdminUserAddress, name='AdminUserAddress'),
    path('user/update/<slug:slug>', users.AdminUserUpdate, name='AdminUserUpdate'),
    path('user/delete/<slug:slug>/', users.AdminUserDelete, name='AdminUserDelete'),
    path('user/setting/<slug:slug>/', users.AdminUserAccountSettings, name='AdminUserAccountSettings'),
    path('user/profile/<slug:slug>/', users.UserPublicProfile, name='UserPublicProfile'),
    path('user/password/<slug:slug>/', users.AdminUserChangePassword, name='AdminUserChangePassword'),
    path('user/deactivate/<slug:slug>/', users.AdminUserDeactivate, name='AdminDeactivateUser'),
    path('user/statements/<slug:slug>', users.UserStatements, name='UserStatements'),
    path('user/billing/<slug:slug>', users.UserBilling, name='UserBilling'),
    path('user/referrals/<slug:slug>', users.UserReferrals, name='UserReferrals'),
    path('dark/', users.UserDarkModeUpdate, name='UserDarkModeUpdate'),
    path('user/geo/', users.AdminUsersGeoInfoList, name='AdminUsersGeoInfoList'),
    path('user/newsletter/', users.AdminUsersNewsletterList, name='AdminUserNewsletter'),
    path('user/contact/', users.AdminClientContactList, name='AdminClientContactList'),
    path('user/contact/detail/<slug:slug>/', users.AdminClientContactDetail, name='AdminClientContactDetails'),
    path('groups/', users.AdminUserGroupList, name='AdminUserGroupList'),
    path('groups/create/', users.AdminUserGroupCreate, name='AdminUserGroupCreate'),
    path('groups/edit/<int:pk>', users.AdminUserGroupEdit, name='AdminUserGroupUpdate'),
    path('groups/delete/<int:id>', users.AdminUserGroupDelete, name='AdminUserGroupDelete'),


    #############################Admin Invoice Urls############################################

    ########## Site Setting Admin #########
    path('site/', core.AdminSiteSettingList, name='AdminSiteSettingList'),
    path('site/detail/<slug:slug>/', core.AdminSiteSettingDetails, name='AdminSiteSettingDetails'),
    path('site/update/<slug:slug>/', core.AdminSiteSettingUpdate, name='AdminSiteSettingUpdate'),
    path('site/delete/<slug:slug>/', core.AdminSiteSettingDelete, name='AdminSiteSettingDelete'),

    ########## System Setting Admin #########
    path('setting/', core.AdminSystemSettingList, name='AdminSystemSettingList'),
    path('setting/detail/<slug:slug>/', core.AdminSystemSettingDetail, name='AdminSystemSettingDetails'),
    path('setting/update<slug:slug>/', core.AdminSystemSettingUpdate, name='AdminSystemSettingUpdate'),
    path('setting/delete/<slug:slug>/', core.AdminSystemSettingDelete, name='AdminSystemSettingDelete'),

    ########## System ConfigSetting Admin #########
    path('config/', core.AdminConfigSettingList, name='AdminConfigSettingList'),
    path('config/detail/<slug:slug>/', core.AdminConfigSettingDetail, name='AdminConfigSettingDetails'),
    path('config/update<slug:slug>/', core.AdminConfigSettingUpdate, name='AdminConfigSettingUpdate'),
    path('config/delete/<slug:slug>/', core.AdminConfigSettingDelete, name='AdminConfigSettingDelete'),


    ########## localization   #########
    path('lang', localization.AdminLanguageList, name='AdminLanguageList'),
    path('lang/update/<slug:slug>/', localization.AdminLanguageUpdate, name='AdminLanguageUpdate'),
    path('lang/delete/<slug:slug>/', localization.AdminLanguageDelete, name='AdminLanguageDelete'),
    path('lang/set/<slug:slug>/', localization.select_language, name='AdminUserSetLanguage'),



    # ########## Qr Code Admin #########
    path('qr/', utilities.AdminQrCodeList, name='AdminQrCodeList'),
    # path('qr/add/', AdminQrCodeCreate.as_view(), name='AdminCreateQrCode'),
    path('qr/detail/<slug:slug>/', utilities.AdminQrCodeDetails, name='AdminQrCodeDetails'),
    path('qr/update/<slug:slug>/', utilities.AdminQrCodeUpdate, name='AdminQrCodeUpdate'),
    path('qr/delete/<slug:slug>/', utilities.AdminQrCodeDelete, name='AdminQrCodeDelete'),




    ##########  Help  Admin #########
    path('help/documentation/', core.AdminHelpDocumentationList, name='AdminHelpDocumentationList'),
    path('help/faq/', core.AdminHelpFaqList, name='AdminHelpFaqList'),
    path('help/tutorial/', core.AdminHelpTutorialList, name='AdminHelpTutorialList'),

    ##########  Help Category Admin #########
    path('help/category/', core.AdminHelpCategoriesList, name='AdminHelpCategoriesList'),
    path('help/category/update/<slug:slug>/', core.AdminHelpCategoriesUpdate, name='AdminHelpCategoriesUpdate'),
    path('help/category/delete/<slug:slug>/', core.AdminHelpCategoriesDelete, name='AdminHelpCategoriesDelete'),
    ##########  Help Questions Admin #########

    path('help/questions/', core.AdminHelpQuestionsList, name='AdminHelpQuestionsList'),
    path('help/questions/add/', core.AdminCreateHelpQuestions, name='AdminHelpQuestionsCreate'),
    path('help/questions/detail/<slug:slug>/', core.AdminHelpQuestionsDetail, name='AdminHelpQuestionsDetails'),
    path('help/questions/update/<slug:slug>/', core.AdminHelpQuestionsUpdate, name='AdminHelpQuestionsUpdate'),
    path('help/questions/delete/<slug:slug>/', core.AdminHelpQuestionsDelete, name='AdminHelpQuestionsDelete'),



    ########### Otp Url ############
    # path('api/otp/setup/', ApiAdminOtpSetupView, name='ApiAdminOtpSetupView'),
    # path('api/otp/qrcode/', ApiAdminOtpQrCodeView, name='ApiAdminOtpQrCodeView'),
    # path('otp/setup/', AdminOtpSetupView.as_view(), name='AdminOtpSetupView'),
    # path('api/otp/otp/', ApiAdminOtpCodeView, name='ApiAdminOtpCodeView'),
    # path('api/otp/verify/', ApiAdminOtpVerifyView, name='ApiAdminOtpVerifyView'),

]
