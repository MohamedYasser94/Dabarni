from django.urls import path


from apps.classified.views import views

app_name = 'classified'

urlpatterns = [

    ########## Classified Category Admin #########
    path('category/', views.AdminJobCategoriesList, name='AdminJobCategoriesList'),
    path('category/edit/<slug:slug>/', views.AdminJobCategoryUpdate, name='AdminJobCategoryUpdate'),
    path('category/delete/<slug:slug>/', views.AdminJobCategoryDelete,
         name='AdminJobCategoryDelete'),



]
