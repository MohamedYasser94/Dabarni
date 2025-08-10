from django.urls import path, include

from api.v1.views import common

app_name = 'api'

urlpatterns = [
    path('jobs/', include('api.v1.job_urls', namespace='job')),
    # Include classified URLs
    path('classified/', include('api.v1.classified_urls', namespace='classified')),

path('search/', common.AdminApiSearch, name='AdminApiSearch'),












]
