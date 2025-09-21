# D:\Python Projects\Dabarni_fork\Dabarni\apps\front\urls.py

from django.urls import path
from .views import views as front_views
app_name="jobtest"
urlpatterns = [
   
    path('register/', front_views.RegisterView, name='register-page'),
    path('confirm-otp/', front_views.ConfirmOTPView, name='confirm-otp-page'),
    path('select-location/', front_views.ChooseLocationView, name='select-location-page'),

    # Client Pages
    path('client/home/', front_views.ClientHomeView, name='client-home-page'),
    path('client/my-jobs/', front_views.my_jobs_view, name='client-my-jobs-page'),
    path('client/job/<int:job_id>/', front_views.job_detail_page, name='client-job-detail-page'),
    path('client/offers/<int:job_id>/',front_views.renderCustomerJobOffersPage, name='client-job-offers'),
    path("client/offers/<int:offer_id>/payment-summary/", front_views.renderCustomerPaymentSummary, name="customer-payment-summary"),
    path('client/offers/<int:offer_id>/confirm-payment/', front_views.renderConfirmPayment, name='customer-confirm-payment'),
    path("client/progress/<int:progress_id>/", front_views.renderJobProgress, name="job_progress"),
    path("client/help/", front_views.help_page, name="client-help-page"),
    path("client/rateProvider/<int:job_id>/",front_views.rate_provider_page,name="rate-provider-page"),

    # Provider Pages
     path('provider/home/', front_views.ProviderHomeView, name='provider-home-page'),
     path('provider/jobs/<int:job_id>/', front_views.renderProviderJobDetailsPage, name='provider-job-details-page'),
     path("provider/rateClient/<int:job_id>/",front_views.rate_customer_page,name="rate-client-page"),
]