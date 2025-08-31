from apps.classified.models.models import *
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




    ################ Job Categories, Locations, Providers and Jobs ########################
    job_categories = JobCategories.objects.filter(parent=None,status='Active').order_by('title')

    job_providers = JobProvider.objects.filter(status='Active')




    context = {

        'job_categories': job_categories,

        'job_providers': job_providers,

               }
    return context

