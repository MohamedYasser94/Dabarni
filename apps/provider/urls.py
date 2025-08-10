from django.urls import path

from apps.provider.views import job, company

app_name = 'provider'

urlpatterns = [

            ################ provider dashboard ################
    path('dashboard', job.ProviderDashboard, name='ProviderDashboard'),

##########  JobProvider  Employee #########
    path('company/employee/', company.ProviderCompanyEmployeeList, name='ProviderCompanyEmployeeList'),
    path('company/employee/add/', company.ProviderCompanyEmployeeCreate, name='ProviderCompanyEmployeeCreate'),
    path('company/employee/edit/<slug:slug>/', company.ProviderCompanyEmployeeUpdate, name='ProviderCompanyEmployeeUpdate'),
    path('company/employee/delete/<slug:slug>/', company.ProviderCompanyEmployeeDelete, name='ProviderCompanyEmployeeDelete'),



    ##########  Job  Admin #########
    path('jobs/', job.ProviderJobList, name='ProviderJobList'),
    path('jobs/add/', job.ProviderJobCreate, name='ProviderJobCreate'),
    path('jobs/edit/<slug:slug>/', job.ProviderJobUpdate, name='ProviderJobUpdate'),
    path('jobs/delete/<slug:slug>/', job.ProviderJobDelete, name='ProviderJobDelete'),



    ########### Requests #########
   path('requests/progress/<str:progress>/', job.AdminJobRequestsList, name='ProviderJobRequestsList'),


    ##################### Job Provider Error Pages #####################
    path('error404/', job.ProviderError404, name='ProviderError404'),



]
