from apps.classified.models.job import *
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

    ########### Classified Categories, Locations, Ads and Reviews #########
    classified_categories = ClassifiedCategories.objects.filter( parent=None, status='Active').order_by('title')
    classified_locations = ClassifiedLocation.objects.filter(status='Active')
    classified_ads = ClassifiedAd.objects.filter(status='New').order_by('-id')
    classified_reviews = ClassifiedReview.objects.filter(status='Active').order_by('-id')


    ################ Job Categories, Locations, Providers and Jobs ########################
    job_categories = JobCategories.objects.filter(parent=None,status='Active').order_by('title')
    job_locations = JobLocation.objects.filter(status='Active')
    job_providers = JobProvider.objects.filter(status='Active')
    jobs = Job.objects.filter(status='Active').order_by('-id')



    context = {
        'classified_categories': classified_categories,
        'classified_locations': classified_locations,
        'classified_ads': classified_ads,
        'classified_reviews': classified_reviews,
        'job_categories': job_categories,
        'job_locations': job_locations,
        'job_providers': job_providers,
        'job_jobs': jobs,
               }
    return context

