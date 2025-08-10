from django.urls import path


from apps.classified.views.job import job,company,ticket

app_name = 'job'

urlpatterns = [



    ##########  Job Catalog  Admin #########
    path('category/', job.AdminJobCategoryList, name='AdminJobCategoryList'),
    path('category/add/', job.AdminJobCategoryCreate, name='AdminJobCategoryCreate'),
    path('category/edit/<slug:slug>/', job.AdminJobCategoryUpdate, name='AdminJobCategoryUpdate'),
    path('category/delete/<slug:slug>/', job.AdminJobCategoryDelete, name='AdminJobCategoryDelete'),

    ##########  JobProvider  Admin #########
    path('provider/', job.AdminJobProviderList, name='AdminJobProviderList'),
    path('provider/add/', job.AdminJobProviderCreate, name='AdminJobProviderCreate'),
    path('provider/edit/<slug:slug>/', job.AdminJobProviderUpdate, name='AdminJobProviderUpdate'),
    path('provider/delete/<slug:slug>/', job.AdminJobProviderDelete, name='AdminJobProviderDelete'),




##########  Job  Admin #########
    path('jobs/', job.AdminJobList, name='AdminJobList'),
    path('jobs/add/', job.AdminJobCreate, name='AdminJobCreate'),
    path('jobs/edit/<slug:slug>/', job.AdminJobUpdate, name='AdminJobUpdate'),
    path('jobs/delete/<slug:slug>/', job.AdminJobDelete, name='AdminJobDelete'),



########### Requests #########
   path('requests/progress/<str:progress>/', job.AdminJobRequestsList, name='AdminJobRequestsList'),


##########  JobProvider Employee #########
    path('provider/employee/', company.AdminJobProviderEmployeeList, name='AdminJobProviderEmployeeList'),
    path('provider/employee/edit/<slug:slug>/', company.AdminJobProviderEmployeeUpdate, name='AdminJobProviderEmployeeUpdate'),
    path('provider/employee/delete/<slug:slug>/', company.AdminJobProviderEmployeeDelete, name='AdminJobProviderEmployeeDelete'),

    ##################### Job Ticket #####################
    path('ticket/', ticket.AdminJobTicketList, name='AdminJobTicketList'),
    path('ticket/details/<slug:slug>/', ticket.AdminJobTicketDetails, name='AdminJobTicketDetails'),

    # URL for the Vue.js app to save admin replies to the Django DB
    path('api/admin/ticket/<slug:ticket_slug>/send_message/', ticket.ApiAdminSaveTicketMessage,
         name='ApiAdminSaveTicketMessage'),

    ######################## Job Report ########################
    path('report/', ticket.AdminJobReportList, name='AdminJobReportList'),
    path('report/details/<slug:report_slug>/', ticket.AdminJobReportDetails, name='AdminJobReportDetails'),

    # FIX: Add the new URL for the admin to save report messages
    path('api/admin/report/<slug:report_slug>/send_message/', ticket.ApiAdminSaveReportMessage,
         name='ApiAdminSaveReportMessage'),










]
