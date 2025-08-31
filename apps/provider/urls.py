from django.urls import path


from apps.provider.views import views

app_name = 'provider'

urlpatterns = [

    ##########  JobProvider  Admin #########
    path('provider/', views.AdminProviderList, name='AdminProviderList'),
    path('provider/details/<slug:slug>/', views.AdminProviderDetails, name='AdminProviderDetails'),
    path('provider/edit/<slug:slug>/', views.AdminProviderUpdate, name='AdminProviderUpdate'),
    path('provider/delete/<slug:slug>/', views.AdminProviderDelete, name='AdminProviderDelete'),



]
