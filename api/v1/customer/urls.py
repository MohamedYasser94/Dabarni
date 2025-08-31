from django.urls import path


from apps.front.views import views, blocks 
from api.v1.customer.views import auth

app_name = 'customer_api'

urlpatterns = [

    path("auth/register/", auth.register, name="register"),
    path("auth/verify-otp/", auth.verify_otp, name="verify-otp"),
    path("save/", auth.save_address, name="save_address"),

]
