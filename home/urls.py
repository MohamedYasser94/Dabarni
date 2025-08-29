from django.urls import path

from apps.wallet.views.payment_gateway import paytabs
from home.views import  views, contact, provider, chat, classified

app_name = 'home'

urlpatterns = [

    path('', views.HomeIndex, name='HomeIndex'),
    path("about/", contact.FrontAbout, name="FrontAbout"),
    path("contact/", contact.ContactFront, name="FrontContact"),
    path("contactform/", contact.FrontContactForm, name="FrontContactForm"),
    path("sendnumber/", contact.FrontSendPhoneForm, name="FrontSendPhoneForm"),
    path("contactform/message_sent", contact.contact_view, name="MessageSent"),
    path("newsletter/", contact.FrontNewsletterSubscriber, name="FrontNewsletterSubscriber"),



    path("faq", views.FAQ, name="FrontFAQ"),
    path("privacypolicy", views.FrontPrivacyPolicy, name="FrontPrivacyPolicy"),
    path("termsofservice", views.FrontTermsOfService, name="FrontTermsOfService"),
    path("termsofservice", views.FrontRequestAQuote, name="FrontRequestAQuote"),
    path("termsconditions", views.FrontTermsConditions, name="FrontTermsConditions"),







    ########### Error Url ###############

    path('403', views.error403, name='Error403'),
    path('404', views.error404, name='Error404'),

    # path('admin/logout', AdminIndex, title='AdminIndex'),

]
