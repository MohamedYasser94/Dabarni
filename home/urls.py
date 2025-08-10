from django.urls import path

from apps.wallet.views.payment_gateway import paytabs
from home.views import blog, views, contact, provider, chat, classified

app_name = 'home'

urlpatterns = [

    path('', views.HomeIndex, name='HomeIndex'),
    path("about/", contact.FrontAbout, name="FrontAbout"),
    path("contact/", contact.ContactFront, name="FrontContact"),
    path("contactform/", contact.FrontContactForm, name="FrontContactForm"),
    path("sendnumber/", contact.FrontSendPhoneForm, name="FrontSendPhoneForm"),
    path("contactform/message_sent", contact.contact_view, name="MessageSent"),
    path("newsletter/", contact.FrontNewsletterSubscriber, name="FrontNewsletterSubscriber"),
    path("vision/", contact.FrontOurVision, name="FrontOurVision"),
    path("portfolio/", contact.FrontOurPortfolio, name="FrontOurPortfolio"),


    path("faq", views.FAQ, name="FrontFAQ"),
    path("privacypolicy", views.FrontPrivacyPolicy, name="FrontPrivacyPolicy"),
    path("termsofservice", views.FrontTermsOfService, name="FrontTermsOfService"),
    path("termsofservice", views.FrontRequestAQuote, name="FrontRequestAQuote"),
    path("termsconditions", views.FrontTermsConditions, name="FrontTermsConditions"),


    ########## Blog Front #########
    path('blog/', blog.FrontBlog, name='FrontBlog'),
    path('blog/<slug:slug>', blog.ArticleDetailFront, name='FrontArticleDetails'),
    path('blog/author/<slug:slug>', blog.AuthorDetailFront, name='FrontArticleAuthorDetails'),
    path('blog/category/<slug:slug>/', blog.ArticleCategoryDetailFront.as_view(), name='FrontArticleCategoryDetails'),
    path('blog/tag/<slug:slug>/', blog.ArticleTagDetailFront.as_view(), name='FrontArticleTagDetails'),


    ############### Classified Front ##############
    path('classified/category'  , classified.FrontClassifiedCategoryList, name='FrontClassifiedCategoryList'),
    path('classified/category/<slug:slug>/' , classified.FrontClassifiedCategoryDetails , name='FrontClassifiedCategoryDetails'),
    path('classified/places'  , classified.FrontClassifiedPlacesList, name='FrontClassifiedPlacesList'),
    path('classified/places/<slug:slug>/' , classified.FrontClassifiedPlacesDetails , name='FrontClassifiedPlacesDetails'),
    path('classified/', classified.FrontClassifiedAdList, name='FrontClassifiedAdList'),
    path('classified/<slug:slug>/', classified.FrontClassifiedAdDetail, name='FrontClassifiedAdDetail'),
path('ad/<slug:slug>/like/', classified.ToggleAdLike, name='ToggleAdLike'),
    # path('classified/<slug:slug>/request/', classified.FrontSubmitClassifiedRequest, name='FrontSubmitClassifiedRequest'),
    # path('classified/<slug:slug>/payment/', classified.FrontClassifiedPayment, name='FrontClassifiedPayment'),
    # path('classified/request/<slug:slug>/upload/', classified.Upload_classified_requirements, name='Upload_classified_requirements'),

############### Job Front ##############
    path('providers/', provider.FrontProviderList, name='FrontJobList'),
    path('providers/job/add/', provider.FrontProviderJobAdd, name='FrontProviderJobAdd'),
    path('providers/category/', provider.FrontProviderCategoryList, name='FrontProviderCategoryList'),
    path('providers/category/<slug:slug>/', provider.FrontProviderCategoryDetail, name='FrontProviderCategoryDetail'),


    ################## Job Provider ##################

    path('providers/jobs/', provider.FrontProviderJobList, name='FrontProviderJobList'),
    path('providers/job/<slug:slug>/', provider.FrontProviderJobDetail, name='FrontProviderJobDetail'),
    path('providers/job/<slug:slug>/request/', provider.FrontSubmitJobRequest, name='FrontSubmitJobRequest'),
    path('providers/job/<slug:slug>/payemnt', provider.FrontProviderJobPayment, name='FrontProviderJobPayment'),
    path('request/<slug:slug>/upload/', provider.Upload_job_requirements, name='Upload_job_requirements'),

    ######## Job Provider Dashboard ##########
    path('providers/dashboard/', provider.FrontProviderDashboard, name='FrontProviderDashboard'),
    path('providers/dashboard/jobs/', provider.FrontProviderJobRequestList, name='FrontProviderJobRequestList'),
    path('providers/dashboard/job/<slug:slug>/edit/', provider.FrontProviderJobEdit, name='FrontProviderJobEdit'),
    path('providers/dashboard/job/reviews/', provider.FrontProviderJobChat, name='FrontProviderJobReviews'),
    path('providers/dashboard/job/chat/', provider.FrontProviderJobChat, name='FrontProviderJobChat'),


    ################# payment ####################
    path('payment-paytabs/<slug:slug>/', paytabs.payment_paytabs, name='PaymentPayTabs'),
    path('api/callbacks-paytabs/', paytabs.api_callback_url_paytabs, name='api_callback_url_paytabs'),
    path('payment-success/', provider.payment_success, name='PaymentSuccess'),

    ########## Chat Admin #########

    # URL to start a chat with a specific user
    path('start-chat/<int:user_id>/', chat.start_chat_view, name='FrontStartChat'),

    # The main chat room URL now accepts a string-based dialog_id
    path('chat/<str:dialog_id>/', chat.chat_room_view, name='FrontChatRoom'),

    # API endpoint to get the list of active dialogs
    path('api/dialogs/', chat.dialog_list_view, name='FrontApiDialogList'),

    # API endpoint for the Firebase Function to save messages
    path('api/save-chat-message/', chat.SaveChatMessageAPI.as_view(), name='save-chat-message'),



    ########### Error Url ###############

    path('403', views.error403, name='Error403'),
    path('404', views.error404, name='Error404'),

    # path('admin/logout', AdminIndex, title='AdminIndex'),

]
