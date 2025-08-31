from django.urls import path


from apps.front.views import views, blocks 
from api.v1.customer.views import auth,profile

app_name = 'customer_api'

urlpatterns = [

    path("auth/register/", auth.register, name="register"),
    path("auth/verify-otp/", auth.verify_otp, name="verify-otp"),
    path("logout/", auth.logout, name="logout"),
    path("save/", auth.save_address, name="save_address"),

    #---------------------- Profile --------------
     path("profile/", profile.GetProfileView.as_view(), name="get-profile"),
    path("profile/update/", profile.UpdateProfileView.as_view(), name="update-profile"),

]
