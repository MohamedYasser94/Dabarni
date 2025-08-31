from django.urls import path


from apps.customer.views import views

app_name = 'customer'

urlpatterns = [
        path('customer/', views.AdminCustomerList, name='AdminCustomerList'),
        path('customer/edit/<slug:slug>/', views.AdminCustomerUpdate, name='AdminCustomerUpdate'),
        path('customer/delete/<slug:slug>/', views.AdminCustomerDelete, name='AdminCustomerDelete')





]
