# D:\Python Projects\Dabarni_fork\Dabarni\apps\front\urls.py

from django.urls import path
from .views import views as front_views

urlpatterns = [
   
    path('register/', front_views.RegisterView, name='register-page'),
    path('confirm-otp/', front_views.ConfirmOTPView, name='confirm-otp-page'),
    path('select-location/', front_views.ChooseLocationView, name='select-location-page'),

    # Client Pages
    path('client/home/', front_views.ClientHomeView, name='client-home-page'),
    path('client/my-jobs/', front_views.my_jobs_view, name='client-my-jobs-page'),
    path('client/job/<int:job_id>/', front_views.job_detail_page, name='client-job-detail-page'),
    path('client/offers/<int:job_id>/',front_views.renderCustomerJobOffersPage, name='client-job-offers'),
    

    # Provider Pages
     path('provider/home/', front_views.ProviderHomeView, name='provider-home-page'),
     path('provider/jobs/<int:job_id>/', front_views.renderProviderJobDetailsPage, name='provider-job-details-page'),
]