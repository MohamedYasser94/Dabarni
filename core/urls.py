from django.urls import path

from api.v1.views import chat as api_chat

from core.utils.export import export_model
from core.views import  blog, chat, core, emails, localization, notifications, users, \
    utilities

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

    path('blog/', blog.BlogDashboard, name='AdminBlogDashboard'),
    path('blog/category/', blog.AdminBlogCategoriesList, name='AdminBlogCategoriesList'),
    path('blog/category/detail/<slug:slug>/', blog.AdminBlogCategoryDetails, name='AdminBlogCategoryDetails'),
    path('blog/category/update/<slug:slug>/', blog.AdminBlogCategoryUpdate, name='AdminBlogCategoryUpdate'),
    path('blog/category/archive/<slug:slug>/', blog.AdminBlogCategoryArchive, name='AdminBlogCategoryArchive'),
    path('blog/category/delete/<slug:slug>/', blog.AdminBlogCategoryDelete, name='AdminBlogCategoryDelete'),

    ########## Tags Admin #########
    path('blog/tags/', blog.AdminBlogTagsList, name='AdminBlogTagsList'),
    path('blog/tags/detail/<slug:slug>/', blog.AdminBlogTagsDetails, name='AdminBlogTagsDetails'),
    path('blog/tags/update/<slug:slug>/', blog.AdminBlogTagsUpdate, name='AdminBlogTagsUpdate'),
    path('blog/tags/archive/<slug:slug>/', blog.AdminBlogTagsArchive, name='AdminBlogTagsArchive'),
    path('blog/tags/delete/<slug:slug>/', blog.AdminBlogTagsDelete, name='AdminBlogTagsDelete'),

    ########## Blog Article Admin #########
    path('blog/article/', blog.AdminBlogArticleList, name='AdminBlogArticleList'),
    path('blog/article/add/', blog.AdminBlogArticleCreate, name='AdminBlogArticleCreate'),
    path('blog/article/detail/<slug:slug>/', blog.AdminBlogArticleDetails, name='AdminBlogArticleDetails'),
    path('blog/article/update/<slug:slug>/', blog.AdminBlogArticleUpdate, name='AdminBlogArticleUpdate'),
    path('blog/article/archive/<slug:slug>/', blog.AdminBlogArticleArchive, name='AdminBlogArticleArchive'),
    path('blog/article/delete/<slug:slug>/', blog.AdminBlogArticleDelete, name='AdminBlogArticleDelete'),
    path('blog/article/images/delete/<slug:slug>/', blog.AdminApiBlogArticleImageDelete, name='AdminApiBlogArticleImageDelete'),


    ########## Services Admin #########
    path('blog/Service/', blog.AdminBlogServicesList, name='AdminBlogServicesList'),
    path('blog/Service/add/', blog.BlogServicesCreate, name='AdminBlogServicesCreate'),
    path('blog/Service/detail/<slug:slug>/', blog.BlogServicesDetail, name='AdminBlogServicesDetails'),
    path('blog/Service/update/<slug:slug>/', blog.BlogServicesUpdate, name='AdminBlogServicesUpdate'),
    path('blog/Service/delete/<slug:slug>/', blog.BlogServicesDelete, name='AdminBlogServicesDelete'),
    path('blog/article/images/delete/<slug:slug>/', blog.AdminApiBlogServicesImageDelete,
         name='AdminApiBlogServicesImageDelete'),

    ########## Inbox Admin #########
    path('inbox/all/<slug:slug>/', emails.AdminEmailList, name='AdminInbox'),
    path('inbox/<slug:slug>/compose/', emails.AdminUserComposeEmail, name='AdminUserComposeEmail'),
    path('inbox/details/<slug:slug>/', emails.AdminDetailsEmail, name='AdminEmailDetails'),
    # path('inbox/<slug:slug>/reply/', emils.AdminReplyEmail, name='AdminReplyEmail'),
    # path('inbox/<slug:slug>/forward/', emils.AdminForwardEmail, name='AdminForwardEmail'),
    # path('inbox/<slug:slug>/delete/', emils.AdminDeleteEmail, name='AdminDeleteEmail'),
    # path('inbox/<slug:slug>/archive/', emils.AdminArchiveEmail, name='AdminArchiveEmail'),
    # path('inbox/<slug:slug>/spam/', emils.AdminSpamEmail, name='AdminSpamEmail'),
    # path('inbox/<slug:slug>/trash/', emils.AdminTrashEmail, name='AdminTrashEmail'),
    # path('inbox/<slug:slug>/restore/', emils.AdminRestoreEmail, name='AdminRestoreEmail'),
    # path('inbox/<slug:slug>/mark_as_read/', emils.AdminMarkAsReadEmail, name='AdminMarkAsReadEmail'),
    # path('inbox/<slug:slug>/mark_as_unread/', emils.AdminMarkAsUnReadEmail, name='AdminMarkAsUnReadEmail'),
    # path('inbox/<slug:slug>/mark_as_important/', emils.AdminMarkAsImportantEmail, name='AdminMarkAsImportantEmail'),
    # path('inbox/<slug:slug>/mark_as_not_important/', emils.AdminMarkAsNotImportantEmail,
    #         name='AdminMarkAsNotImportantEmail'),
    # path('inbox/<slug:slug>/mark_as_starred/', emils.AdminMarkAsStarredEmail, name='AdminMarkAsStarredEmail'),
    # path('inbox/<slug:slug>/mark_as_unstarred/', emils.AdminMarkAsUnStarredEmail, name='AdminMarkAsUnStarredEmail'),
    # path('inbox/<slug:slug>/mark_as_spam/', emils.AdminMarkAsSpamEmail, name='AdminMarkAsSpamEmail'),
    # path('inbox/<slug:slug>/mark_as_not_spam/', emils.AdminMarkAsNotSpamEmail, name='AdminMarkAsNotSpamEmail'),


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

    path('country', localization.AdminCountryList, name='AdminCountryList'),
    path('country/update/<slug:slug>/', localization.AdminCountryUpdate, name='AdminCountryUpdate'),
    path('country/delete/<slug:slug>/', localization.AdminCountryDelete, name='AdminCountryDelete'),

    path('<slug:slug>/governorates/', localization.AdminGovernoratesList, name='AdminGovernoratesList'),
    path('<slug:slug>/governorates/update/<slug:g_slug>/', localization.GovernoratesUpdate,
         name='AdminGovernoratesUpdate'),
    path('<slug:slug>/governorates/delete/<slug:g_slug>/', localization.GovernoratesDelete,
         name='AdminGovernoratesDelete'),

    path('<slug:slug>/city/', localization.AdminCityList, name='AdminCityList'),
    path('<slug:slug>/city/update/<slug:c_slug>/', localization.AdminCityUpdate, name='AdminCityUpdate'),
    path('<slug:slug>/city/delete/<slug:c_slug>/', localization.AdminCityDelete, name='AdminCityDelete'),

    path('<slug:slug>/area/', localization.AdminAreaList, name='AdminAreaList'),
    path('<slug:slug>/area/update/<slug:a_slug>/', localization.AdminAreaUpdate, name='AdminAreaUpdate'),
    path('<slug:slug>/area/delete/<slug:a_slug>/', localization.AdminAreaDelete, name='AdminAreaDelete'),

    path('currency', localization.AdminCurrencyList, name='AdminCurrencyList'),
    path('currency/add/', localization.AdminCurrencyCreate, name='AdminCurrencyCreate'),
    path('currency/<slug:slug>/', localization.AdminCurrencyDetails, name='AdminCurrencyDetails'),
    path('currency/update/<slug:slug>/', localization.AdminCurrencyUpdate, name='AdminCurrencyUpdate'),
    path('currency/delete/<slug:slug>/', localization.AdminCurrencyDelete, name='AdminCurrencyDelete'),

    # ########## Qr Code Admin #########
    path('qr/', utilities.AdminQrCodeList, name='AdminQrCodeList'),
    # path('qr/add/', AdminQrCodeCreate.as_view(), name='AdminCreateQrCode'),
    path('qr/detail/<slug:slug>/', utilities.AdminQrCodeDetails, name='AdminQrCodeDetails'),
    path('qr/update/<slug:slug>/', utilities.AdminQrCodeUpdate, name='AdminQrCodeUpdate'),
    path('qr/delete/<slug:slug>/', utilities.AdminQrCodeDelete, name='AdminQrCodeDelete'),

    ########## Coupon Admin #########
    path('coupon/', utilities.AdminCouponList, name='AdminCouponList'),
    path('coupon/detail/<slug:slug>/', utilities.AdminCouponDetails, name='AdminCouponDetails'),
    path('coupon/update/<slug:slug>/', utilities.AdminCouponUpdate, name='AdminCouponUpdate'),
    path('coupon/delete/<slug:slug>/', utilities.AdminCouponDelete, name='AdminCouponDelete'),

    ########## Membership Admin #########
    path('membership/', utilities.AdminMembershipList, name='AdminMembershipList'),
    path('membership/detail/<slug:slug>/', utilities.AdminMembershipDetails, name='AdminMembershipDetails'),
    path('membership/update/<slug:slug>/', utilities.AdminMembershipUpdate, name='AdminMembershipUpdate'),
    path('membership/archive/<slug:slug>/', utilities.AdminMembershipArchive, name='AdminMembershipArchive'),
    path('membership/delete/<slug:slug>/', utilities.AdminMembershipArchive, name='AdminMembershipDelete'),

    ########## Subscription Admin #########
    path('subscription/', utilities.AdminSubscriptionList, name='AdminSubscriptionList'),
    path('subscription/detail/<slug:slug>/', utilities.AdminSubscriptionDetails, name='AdminSubscriptionDetails'),
    path('subscription/update/<slug:slug>/', utilities.AdminSubscriptionUpdate, name='AdminSubscriptionUpdate'),
    path('subscription/archive/<slug:slug>/', utilities.AdminSubscriptionArchive, name='AdminSubscriptionArchive'),

    ########## Subscription Payment Admin #########
    path('subscriptionpayment/', utilities.AdminSubscriptionPaymentList, name='AdminSubscriptionPaymentList'),

    path('subscriptionpayment/detail/<slug:slug>/', utilities.AdminSubscriptionDetails,
         name='AdminSubscriptionPaymentDetails'),
    path('subscriptionpayment/update/<slug:slug>/', utilities.AdminSubscriptionUpdate,
         name='AdminSubscriptionPaymentUpdate'),
    path('subscriptionpayment/archive/<slug:slug>/', utilities.AdminSubscriptionArchive,
         name='AdminSubscriptionPaymentArchive'),




    ###############Utility Admin ###############
    path('export_model', export_model, name='AdminExportModel'),

    ########## Chat Admin #########

    # URL to start a chat with a specific user
    path('start-chat/<int:user_id>/', chat.start_chat_view, name='start_chat'),

    # The main chat room URL
    path('chat/<uuid:dialog_id>/', chat.chat_room_view, name='chat_room'),

    # API endpoint to get the list of active dialogs for the current user
    path('api/dialogs/', chat.dialog_list_view, name='api_dialog_list'),



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
