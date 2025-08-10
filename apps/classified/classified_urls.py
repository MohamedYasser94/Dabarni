from django.urls import path

from apps.classified.views.classified import classified

app_name = 'classified'

urlpatterns = [

    ########## Classified Category Admin #########
    path('category/', classified.AdminClassifiedCategoriesList, name='AdminClassifiedCategoriesList'),
    # path('category/create/', classified.AdminClassifiedCategoryCreate, name='AdminClassifiedCategoryCreate'),
    path('category/edit/<slug:slug>/', classified.AdminClassifiedCategoryUpdate, name='AdminClassifiedCategoryUpdate'),
    path('category/delete/<slug:slug>/', classified.AdminClassifiedCategoryDelete, name='AdminClassifiedCategoryDelete'),

    ################# ClassifiedLocation ########################
    path('location/', classified.AdminClassifiedLocationList, name='AdminClassifiedLocationList'),
    # path('location/create/', classified.AdminClassifiedLocationCreate, name='AdminClassifiedLocationCreate'),
    path('location/edit/<slug:slug>/', classified.AdminClassifiedLocationUpdate, name='AdminClassifiedLocationUpdate'),
    path('location/delete/<slug:slug>/', classified.AdminClassifiedLocationDelete, name='AdminClassifiedLocationDelete'),

    ################# ClassifiedAd ########################
    path('ad/', classified.AdminClassifiedAdList, name='AdminClassifiedAdList'),
    path('ad/create/', classified.AdminClassifiedAdCreate, name='AdminClassifiedAdCreate'),
    path('ad/edit/<slug:slug>/', classified.AdminClassifiedAdUpdate, name='AdminClassifiedAdUpdate'),
    path('ad/delete/<slug:slug>/', classified.AdminClassifiedAdDelete, name='AdminClassifiedAdDelete'),



    ################# PromotedClassifiedAd ########################
    path('promoted-ad/', classified.AdminPromotedClassifiedAdList, name='AdminPromotedClassifiedAdList'),
    path('promoted-ad/create/', classified.AdminPromotedClassifiedAdCreate, name='AdminPromotedClassifiedAdCreate'),
    path('promoted-ad/edit/<slug:slug>/', classified.AdminPromotedClassifiedAdUpdate, name='AdminPromotedClassifiedAdUpdate'),
    path('promoted-ad/delete/<slug:slug>/', classified.AdminPromotedClassifiedAdDelete, name='AdminPromotedClassifiedAdDelete'),



    ################# ClassifiedReview ########################
    path('review/', classified.AdminClassifiedReviewList, name='AdminClassifiedReviewList'),
    path('review/edit/<slug:slug>/', classified.AdminClassifiedReviewUpdate, name='AdminClassifiedReviewUpdate'),
    path('review/delete/<slug:slug>/', classified.AdminClassifiedReviewDelete, name='AdminClassifiedReviewDelete'),

################# PromotedClassifiedAd ########################
    path('promoted-ad/', classified.AdminPromotedClassifiedAdList, name='AdminPromotedClassifiedAdList'),
    path('promoted-ad/create/', classified.AdminPromotedClassifiedAdCreate, name='AdminPromotedClassifiedAdCreate'),
    path('promoted-ad/edit/<slug:slug>/', classified.AdminPromotedClassifiedAdUpdate, name='AdminPromotedClassifiedAdUpdate'),
    path('promoted-ad/delete/<slug:slug>/', classified.AdminPromotedClassifiedAdDelete, name='AdminPromotedClassifiedAdDelete'),


    ################# UserSearch ########################
    path('user-search/', classified.AdminUserSearchList, name='AdminUserSearchList'),

    ################# UserSavedSearch ########################
    path('user-saved-search/', classified.AdminUserSavedSearchList, name='AdminUserSavedSearchList'),

    ################# Commercials ########################
    path('commercials/', classified.AdminCommercialsList, name='AdminCommercialsList'),
    path('commercials/create/', classified.AdminCommercialsCreate, name='AdminCommercialsCreate'),
    path('commercials/edit/<slug:slug>/', classified.AdminCommercialsUpdate, name='AdminCommercialsUpdate'),
    path('commercials/delete/<slug:slug>/', classified.AdminCommercialsDelete, name='AdminCommercialsDelete'),
]