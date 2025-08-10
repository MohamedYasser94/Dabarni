from django.contrib.auth import get_user_model

from apps.classified.models.job import *
from core.models.core import CommonTranslate
from helper.decorators import authenticated_staff, staff_only

User = get_user_model()


##########  Car Garage Admin #########
@authenticated_staff
@staff_only
def AdminIndexCatalogAppData(request):
    current_user = User.objects.get(id=request.user.id)
    user_group = User.objects.get(id=request.user.id).groups

    context = {

    }

    return context


def AdminGetCurrentUser(request):
    check_current_user = User.objects.get(id=request.user.id)



def FrontIndexClassifiedAppData(request):
    categories = JobCategories.objects.filter(parent=None,status='Active').order_by('title')
    locations = JobLocation.objects.filter(status='Active')
    providers = JobProvider.objects.filter(status='Active')
    jobs = Job.objects.filter(status='Active').order_by('-id')



    context = {
        'categories': categories,
        'locations': locations,
        'providers': providers,
        'jobs': jobs,
               }
    return context

