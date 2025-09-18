from django.urls import path


from apps.classified.views import views, job_management_views 

app_name = 'classified'

urlpatterns = [

    ########## Classified Category Admin #########
    path('category/', views.AdminJobCategoriesList, name='AdminJobCategoriesList'),
    path('category/edit/<slug:slug>/', views.AdminJobCategoryUpdate, name='AdminJobCategoryUpdate'),
    path('category/delete/<slug:slug>/', views.AdminJobCategoryDelete, name='AdminJobCategoryDelete'),

    #----------------------------------------------------------
    path('jobs/all/', job_management_views.AdminJobList, name='AdminJobList'),
    path('jobs/active/', job_management_views.AdminActiveJobs, name='AdminActiveJobs'),
    path('jobs/completed/', job_management_views.AdminCompletedJobs, name='AdminCompletedJobs'),
    path('jobs/canceled/', job_management_views.AdminCanceledJobs, name='AdminCanceledJobs'),
    path('offers/', job_management_views.AdminManageOffers, name='AdminManageOffers'),
    path('negotiations/', job_management_views.AdminManageNegotiations, name='AdminManageNegotiations'),


]
