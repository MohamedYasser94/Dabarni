from django.urls import path


from apps.front.views import views, blocks 
from api.v1.customer.views import profile ,jop , category

app_name = 'customer_api'

urlpatterns = [

   
    path("customer/address/",profile.save_address, name="save-address"),
    path("customer/address/list/",profile.list_addresses, name="list-addresses"),
    path("customer/address/<int:pk>/delete/",profile.delete_address, name="delete-address"),
    #---------------------- Profile --------------
     path("profile/", profile.GetProfileView.as_view(), name="get-profile"),
     path("profile/update/", profile.UpdateProfileView.as_view(), name="update-profile"),
     path("addresses/", profile.list_addresses, name="list-addresses"), 
     path("addresses/<int:pk>/delete/", profile.delete_address, name="delete-address"),

     # -------------------- Jobs ----------------------------------  
      # Path for creating a new job
    path('jobs/create/', jop.create_job, name='customer-job-create'),
    # Path for listing jobs of the current user
    path('jobs/my/', jop.list_my_jobs, name='customer-jobs-list'),
    # Path for retrieving a single job by ID
    path('jobs/<int:job_id>/', jop.retrieve_job, name='customer-job-retrieve'),
    path('jobs/status/<str:status_param>/', jop.list_jobs_by_progress_status, name='customer-jobs-by-status'),
    path('jobs/<int:job_id>/cancel/', jop.cancel_job, name='customer-job-cancel'),
    path('jobs/<int:job_id>/offers/', jop.getOffersByJob, name='customer-job-offers'),
    path('offers/<int:offer_id>/accept/', jop.customerAcceptOffer, name='customer-accept-offer'),
    #--------------------- Category ----------------------------
     path("categories/", category.list_categories, name="category-list"),
     path("categories/<slug:slug>/", category.retrieve_category, name="category-detail"),
      

]
