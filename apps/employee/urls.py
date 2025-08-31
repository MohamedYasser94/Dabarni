from django.urls import path


from apps.employee.views import views

app_name = 'employee'

urlpatterns = [

    path('employee/', views.AdminEmployeeList, name='AdminEmployeeList'),
    path('employee/edit/<slug:slug>/', views.AdminEmployeeUpdate, name='AdminEmployeeUpdate'),
    path('employee/delete/<slug:slug>/', views.AdminEmployeeDelete, name='AdminEmployeeDelete')



]
