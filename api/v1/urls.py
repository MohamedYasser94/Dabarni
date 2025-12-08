from django.urls import path
from api.v1 import authentication

app_name = 'app_api'

urlpatterns = [

    path("auth/register/", authentication.register, name="register"),
    path("auth/verify-otp/", authentication.verify_otp, name="verify-otp"),
    path("logout/", authentication.logout, name="logout"),
]
