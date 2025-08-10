from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from apps.classified.models.classified import ClassifiedCategories, ClassifiedAd, ClassifiedLocation
from helper.commonHelper import ACTIVE_FRONTEND_TEMPLATES


def FrontClassifiedCategoryList(request):
    category = ClassifiedCategories.objects.filter(parent=None,status='Active').order_by('title')
    classified_locations = ClassifiedLocation.objects.filter( status='Active').order_by('-id')
    context = {
        'category': category,
        'classified_locations': classified_locations,
    }

    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/classified/category_list.html',context )

def FrontClassifiedCategoryDetails(request,slug):
    category = ClassifiedCategories.objects.get(slug=slug)
    context = {
        'category': category,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/classified/category_details.html',context )


def FrontClassifiedPlacesList(request):
    category = ClassifiedCategories.objects.all()
    locations = ClassifiedLocation.objects.filter(status='Active').order_by('-id')
    context = {
        'category': 'places',
        'locations': locations,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/classified/classified_list.html',context )

def FrontClassifiedPlacesDetails(request,slug):
    category = ClassifiedCategories.objects.get(slug=slug)
    context = {
        'category': category,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/classified/classified_details.html',context )


def FrontClassifiedAdList(request):
    category = ClassifiedCategories.objects.all()
    context = {
        'category': 'ads',
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/classified/classified_list.html',context )


def FrontClassifiedAdDetail(request, slug):
    category = ClassifiedCategories.objects.get(slug=slug)
    context = {
        'category': category,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/classified/classified_details.html',context )


@login_required
def ToggleAdLike(request, slug):
    if request.method == 'POST':
        ad = get_object_or_404(ClassifiedAd, slug=slug)
        user = request.user

        # Toggle like status
        if user in ad.likes.all():
            ad.likes.remove(user)
            liked = False
        else:
            ad.likes.add(user)
            liked = True

        # Sync the like field (optional, only if used elsewhere)
        ad.get_incremented_likes()

        # Return JSON response with like status and count
        return JsonResponse({
            'liked': liked,
            'likes_count': ad.get_like_count()
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)