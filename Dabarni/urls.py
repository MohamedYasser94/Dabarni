"""Dabarni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.v1 import authentication

from home.views.chat import dialog_list_view

schema_view = get_schema_view(openapi.Info(title="Ddigithup API", default_version='v1', description="Test description",
                                           terms_of_service="https://www.google.com/policies/terms/",
                                           contact=openapi.Contact(email="contact@snippets.local"),
                                           license=openapi.License(name="BSD License"), ), public=True,
                              permission_classes=[permissions.AllowAny], )

urlpatterns = [path('i18n/', include('django.conf.urls.i18n')),

    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

     path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
     path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path('api/v1/customer/', include('api.v1.customer.urls'), name='customer_api'),
    path('api/v1/provider/', include('api.v1.provider.urls'), name='provider_api'),
    path('auth/', include([
        path('register/', authentication.register, name='auth-register'),
        path('verify-otp/', authentication.verify_otp, name='auth-verify-otp'),
        path('logout/', authentication.logout, name='auth-logout'),
    ]), name='authentication_api'),
 
]

urlpatterns += i18n_patterns(

    path('dashboard/', include('core.urls'), name='core'),
    path('dashboard/classified/', include('apps.classified.urls'), name='classified'),
    path('dashboard/customer/', include('apps.customer.urls'), name='customer'),
    path('test/', include('apps.TEST_PROCESS.urls'), name='test_process'),
    path('dashboard/employee/', include('apps.employee.urls'), name='employee'),
    path('dashboard/front/', include('apps.front.urls'), name='front'),
    path('dashboard/provider/', include('apps.provider.urls'), name='provider'),
    path('dashboard/wallet/', include('apps.wallet.urls'), name='wallet'),
    path('', include('home.urls'), name='home'),
    path('', include('user.urls', namespace='user')),
    path('api/dialogs/', dialog_list_view, name='dialog_list'),

    # path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    prefix_default_language=True

)

handler404 = "home.views.views.error404"
handler500 = 'home.views.views.server_error_view'
handle403 = 'home.views.views.permission_denied_view'

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r'^rosetta/', include('rosetta.urls'))]
