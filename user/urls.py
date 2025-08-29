from django.urls import path

from user.views.profile import FrontUserProfile, FrontUpdateProfile, \
    FrontLoginUserProfile
from user.views.user import UserActivate, UserLogin, UserLogout, TestPages, \
    resend_activation_email, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, facebook_login, google_login, CustomerRegister

app_name = 'user'

urlpatterns = [

    # path('guest-user/', guest_user_view, title='guest_user_register'),

    ##########User################
    path('signup/', CustomerRegister, name='FrontCustomerRegister'),
    path('login/', UserLogin.as_view(), name='FrontCustomerLogin'),
    path('logout/', UserLogout, name='FrontCustomerLogout'),
    path('activate/<uidb64>/<token>/', UserActivate, name='activate'),
    path('reactivate/', resend_activation_email, name='CustomerResendActivationEmail'),

    path('social/fb', facebook_login, name='CustomerFaceBookLogin'),
    path('social/google', google_login, name='CustomerGoogleLogin'),

    path('test/', TestPages, name='TestPages'),
    #

    ##################UserProfile#################
    path('user/profile/', FrontUserProfile, name='FrontUserProfile'),
    path('user/myprofile/<slug:slug>', FrontLoginUserProfile, name='FrontLoginUserProfile'),

    path('user/uprofile/<slug:slug>', FrontUpdateProfile, name='FrontUpdateProfile'),


    # ###########Password###########
    #
    path('reset/', PasswordResetView.as_view(), name="FrontResetPassword"),
    path('reset/sent/', PasswordResetDoneView.as_view(), name="FrontPasswordResetDone"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="FrontPasswordResetConfirm"),
    path('reset/complete/', PasswordResetCompleteView.as_view(), name="FrontPasswordResetComplete"),



]
