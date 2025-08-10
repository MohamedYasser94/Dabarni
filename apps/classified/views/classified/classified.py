from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Assumption: Your models are in one of these locations. Adjust as needed.
from apps.classified.models.classified import (
    ClassifiedCategories,
    ClassifiedLocation,
    ClassifiedAd,
    ClassifiedAdItem,
    ClassifiedMedia,
    AdAttribute,
    PromotedClassifiedAd,
    Favorite,
    ClassifiedReview,
    UserSearch,
    UserSavedSearch,
    Commercials
)
# Assumption: Your forms are in a forms directory. You must create these forms.
from apps.classified.forms.classified import (
    AdminClassifiedCategoryForm,
    AdminClassifiedLocationForm,
    AdminClassifiedAdForm,
    AdminClassifiedAdItemForm,
    AdminClassifiedMediaForm,
    AdminAdAttributeForm,
    AdminPromotedClassifiedAdForm,
    AdminFavoriteForm,
    AdminClassifiedReviewForm,
    AdminCommercialsForm
)
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()


########################## Classified Category Admin ################################
# Note: These are the functions you provided as a reference.

@authenticated_staff
@staff_only
def AdminClassifiedCategoriesList(request):
    categories = ClassifiedCategories.objects.all()
    if request.method == "POST":
        # This view combines List and Create functionality.
        category_form = AdminClassifiedCategoryForm(request.POST or None, request.FILES or None)
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            job_category = request.POST.get('job_category')

            category_object = ClassifiedCategories(
                title=title,
                keyword=keyword,
                image=image,
                job_category=job_category
            )
            category_object.save()

            messages.success(request, _("Category Added Successfully"), extra_tags='Category')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoriesList'))
        else:
            messages.error(request, _("Category Not Added, Please Try Again"), extra_tags='Category')

    context = {
        'categories': categories,
        'category_form': AdminClassifiedCategoryForm(),
        'current_page': _('Categories')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/admin.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedCategoryUpdate(request, slug):
    category = ClassifiedCategories.objects.get(slug=slug)
    category_form = AdminClassifiedCategoryForm(request.POST or None, request.FILES or None, instance=category)

    if request.method == "POST":
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            job_category = request.POST.get('job_category')
            parent = request.POST.get('parent')
            status = request.POST.get('status')

            if parent:
                parent_category = ClassifiedCategories.objects.get(id=parent)
                if parent_category.slug == slug:
                    messages.error(request, _("Parent category cannot be the same as the current category."), extra_tags='Category')
                    return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoryUpdate', kwargs={'slug': slug}))
            else:
                parent_category = None


            category_object = ClassifiedCategories.objects.get(slug=slug)
            category_object.title = title
            category_object.keyword = keyword
            category_object.image = image
            category_object.job_category = job_category
            category_object.parent = parent_category
            category_object.status = status
            category_object.save()
            messages.success(request, _("Category Updated Successfully"), extra_tags='Category')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoriesList'))
        else:
            messages.error(request, _("Category Not Updated, Please Try Again"), extra_tags='Category')

    context = {
        'category': category,
        'category_form': category_form,
        'current_page': _('Categories')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/update.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedCategoryDelete(request, slug):
    category = ClassifiedCategories.objects.get(slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category Deleted Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoriesList'))

    context = {
        'item_to_delete': category,
        'current_page': _('Categories')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/delete.html', context)


########################## ClassifiedLocation Admin ################################

@authenticated_staff
@staff_only
def AdminClassifiedLocationList(request):
    locations = ClassifiedLocation.objects.all()
    if request.method == "POST":
        location_form = AdminClassifiedLocationForm(request.POST or None ,request.FILES or None, )
        if location_form.is_valid():
            location_form.save()
            messages.success(request, _("Location Added Successfully"), extra_tags='Location')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedLocationList'))
        else:
            messages.error(request, _("Location Not Added, Please Try Again"), extra_tags='Location')

    context = {
        'locations': locations,
        'location_form': AdminClassifiedLocationForm(),
        'current_page': _('Locations')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/location/admin.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedLocationUpdate(request, slug):
    location = ClassifiedLocation.objects.get(slug=slug)
    location_form = AdminClassifiedLocationForm(request.POST or None ,request.FILES or None,instance=location)

    if request.method == "POST":
        if location_form.is_valid():
            location_form.save()
            messages.success(request, _("Location Updated Successfully"), extra_tags='Location')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedLocationList'))
        else:
            messages.error(request, _("Location Not Updated, Please Try Again"), extra_tags='Location')

    context = {
        'location': location,
        'location_form': location_form,
        'current_page': _('Locations')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/location/update.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedLocationDelete(request, slug):
    location = ClassifiedLocation.objects.get(slug=slug)
    if request.method == "POST":
        location.delete()
        messages.success(request, _("Location Deleted Successfully"), extra_tags='Location')
        return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedLocationList'))

    context = {
        'item_to_delete': location,
        'current_page': _('Locations')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/location/delete.html', context)


########################## ClassifiedAd Admin ################################

@authenticated_staff
@staff_only
def AdminClassifiedAdList(request):
    ads = ClassifiedAd.objects.all()



    context = {
        'ads': ads,
        'ad_form': AdminClassifiedAdForm(),
        'current_page': _('Classified Ads')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/ad/admin.html', context)


@authenticated_staff
@staff_only
@transaction.atomic
def AdminClassifiedAdCreate(request):
    """
    Handles the creation of a new Classified Ad.
    This version is corrected to properly handle flat repeater data from the form.
    """
    if request.method == "POST":
        try:
            print('request' ,request.POST)
            # --- 1. Manually Create the Main ClassifiedAd Object ---
            ad_object = ClassifiedAd(
                user=request.user,
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category_id=request.POST.get('category'),
                location_id=request.POST.get('location'),
                price=request.POST.get('price') or None,
                hide_price=request.POST.get('hide_price'),
                number=request.POST.get('number'),
                hide_number=request.POST.get('hide_number'),
                whats_app_number=request.POST.get('whats_app_number'),
                whats_app_hide_number=request.POST.get('whats_app_hide_number'),
                negotiable=request.POST.get('negotiable'),
                is_featured=request.POST.get('is_featured'),
                is_premium=request.POST.get('is_premium'),
                is_urgent=request.POST.get('is_urgent'),
                is_promoted=request.POST.get('is_promoted'),
                is_featured_top=request.POST.get('is_featured_top'),
                is_featured_bottom=request.POST.get('is_featured_bottom'),
                is_featured_left=request.POST.get('is_featured_left'),
                is_featured_right=request.POST.get('is_featured_right'),
                is_featured_slider=request.POST.get('is_featured_slider'),
                is_featured_banner=request.POST.get('is_featured_banner'),
                is_featured_category=request.POST.get('is_featured_category'),
                is_featured_search=request.POST.get('is_featured_search'),
                is_featured_home=request.POST.get('is_featured_home'),
                is_featured_sidebar=request.POST.get('is_featured_sidebar'),
                latitude=request.POST.get('latitude') or None,
                longitude=request.POST.get('longitude') or None,
                image=request.FILES.get('image')
            )
            ad_object.save()


            # --- 2. Process Ad Items from Repeater ---
            item_names = request.POST.getlist('[item_name]')
            item_descriptions = request.POST.getlist('[item_description]')
            item_prices = request.POST.getlist('[item_price]')
            item_images = request.FILES.getlist('[item_image]')

            for i, (name, desc, price) in enumerate(zip(item_names, item_descriptions, item_prices)):
                if name.strip():
                    item = ClassifiedAdItem(
                        classified_ad=ad_object,
                        item_name=name,
                        item_description=desc,
                        item_price=price or None
                    )
                    if i < len(item_images):
                        item.item_image = item_images[i]
                    item.save()

            # --- 3. Process Custom Attributes from Repeater ---
            attribute_names = request.POST.getlist('[attribute_name]')
            attribute_values = request.POST.getlist('[attribute_value]')

            for name, value in zip(attribute_names, attribute_values):
                if name.strip():
                    adAttribute_objct= AdAttribute(
                        classified_ad=ad_object,
                        name=name,
                        value=value
                    )
                    adAttribute_objct.save()



            # --- 4. Process Media Gallery ---
            gallery_images = request.FILES.getlist('gallery_images')
            ad_content_type = ContentType.objects.get_for_model(ad_object)
            for image_file in gallery_images:
                ClassifiedMedia.objects.create(
                    owner_model=ad_content_type,
                    owner_id=ad_object.id,
                    image=image_file,
                    type='Image'
                )

            messages.success(request, _("Classified Ad created successfully!"), extra_tags='ClassifiedAd')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedAdList'))

        except Exception as e:
            messages.error(request, _(f"An error occurred: {e}"), extra_tags='ClassifiedAd')

    context = {'ad_form': AdminClassifiedAdForm()}
    return render(request, f'{BACKEND_TEMPLATES}/classified/ad/add.html', context)




@authenticated_staff
@staff_only
@transaction.atomic
def AdminClassifiedAdUpdate(request, slug):
    """
    Handles the update of an existing Classified Ad by manually processing POST data
    to bypass strict form validation, consistent with the create function.
    """
    ad = get_object_or_404(ClassifiedAd, slug=slug)

    if request.method == "POST":
        try:
            # --- 1. Update the Main ClassifiedAd Object ---
            # Manually update fields, bypassing form.is_valid()
            ad.title = request.POST.get('title')
            ad.description = request.POST.get('description')
            ad.category_id = request.POST.get('category')
            ad.location_id = request.POST.get('location')
            ad.price = request.POST.get('price') or None
            ad.hide_price = request.POST.get('hide_price') 
            ad.number = request.POST.get('number')
            ad.hide_number = request.POST.get('hide_number') 
            ad.whats_app_number = request.POST.get('whats_app_number')
            ad.whats_app_hide_number = request.POST.get('whats_app_hide_number') 
            ad.negotiable = request.POST.get('negotiable') 
            ad.status = request.POST.get('status', 'Active')  # Default to 'Active' if not provided

            # Promotion flags
            ad.is_featured = request.POST.get('is_featured')
            ad.is_premium = request.POST.get('is_premium') 
            ad.is_urgent = request.POST.get('is_urgent') 
            ad.is_promoted = request.POST.get('is_promoted') 
            ad.is_featured_top = request.POST.get('is_featured_top') 
            ad.is_featured_bottom = request.POST.get('is_featured_bottom') 
            ad.is_featured_left = request.POST.get('is_featured_left') 
            ad.is_featured_right = request.POST.get('is_featured_right') 
            ad.is_featured_slider = request.POST.get('is_featured_slider') 
            ad.is_featured_banner = request.POST.get('is_featured_banner') 
            ad.is_featured_category = request.POST.get('is_featured_category') 
            ad.is_featured_search = request.POST.get('is_featured_search') 
            ad.is_featured_home = request.POST.get('is_featured_home') 
            ad.is_featured_sidebar = request.POST.get('is_featured_sidebar') 

            ad.latitude = request.POST.get('latitude') or None
            ad.longitude = request.POST.get('longitude') or None

            # Handle main image upload
            if 'image' in request.FILES:
                ad.image = request.FILES.get('image')

            ad.save()

            print('requst',request.POST)

            # --- 2. Process Existing Items (Update/Delete) ---
            item_slugs = request.POST.getlist('itemu_slug')
            item_names = request.POST.getlist('itemu_name')
            item_descriptions = request.POST.getlist('itemu_description')
            item_prices = request.POST.getlist('itemu_price')
            items_to_delete = request.POST.getlist('itemu_delete')
            item_images = {key: value for key, value in request.FILES.items() if key.startswith('itemu_image_')}

            for i, item_slug in enumerate(item_slugs):
                if item_slug in items_to_delete:
                    ClassifiedAdItem.objects.filter(slug=item_slug, classified_ad=ad).delete()
                else:
                    item = ClassifiedAdItem.objects.get(slug=item_slug, classified_ad=ad)
                    item.item_name = item_names[i]
                    item.item_description = item_descriptions[i]
                    item.item_price = item_prices[i] or None
                    # Handle item image update
                    image_key = f'item_image_{item_slug}'
                    if image_key in item_images:
                        item.item_image = item_images[image_key]
                    item.save()

            # --- 3. Process New Items ---
            new_item_names = request.POST.getlist('[item_name]')
            new_item_descriptions = request.POST.getlist('[item_description]')
            new_item_prices = request.POST.getlist('[item_price]')
            new_item_images = request.FILES.getlist('[item_image]')

            for i, name in enumerate(new_item_names):
                if name.strip():
                    item = ClassifiedAdItem.objects.create(
                        classified_ad=ad,
                        item_name=name,
                        item_description=new_item_descriptions[i],
                        item_price=new_item_prices[i] or None
                    )
                    if i < len(new_item_images):
                        item.item_image = new_item_images[i]
                        item.save()

            # --- 4. Process Attributes (Update/Delete/Create) ---
            attribute_slugs = request.POST.getlist('attributeu_slug')
            attribute_names = request.POST.getlist('attributeu_name')
            attribute_values = request.POST.getlist('attributeu_value')
            attributes_to_delete = request.POST.getlist('attributeu_delete')

            for i, attr_slug in enumerate(attribute_slugs):
                if attr_slug in attributes_to_delete:
                    AdAttribute.objects.filter(slug=attr_slug, classified_ad=ad).delete()
                else:
                    attr = AdAttribute.objects.get(slug=attr_slug, classified_ad=ad)
                    attr.name = attribute_names[i]
                    attr.value = attribute_values[i]
                    attr.save()

            new_attribute_names = request.POST.getlist('[attribute_name]')
            new_attribute_values = request.POST.getlist('[attribute_value]')
            for i, name in enumerate(new_attribute_names):
                if name.strip():
                    attr_object = AdAttribute(
                        classified_ad=ad,
                        name=name,
                        value=new_attribute_values[i]
                    )
                    attr_object.save()

            # --- 5. Process Media Gallery (Delete/Add) ---
            media_to_delete = request.POST.getlist('media_delete')
            ClassifiedMedia.objects.filter(slug__in=media_to_delete, owner_id=ad.id).delete()

            new_gallery_images = request.FILES.getlist('new_gallery_images')
            ad_content_type = ContentType.objects.get_for_model(ad)
            for image_file in new_gallery_images:
                ClassifiedMedia.objects.create(
                    owner_model=ad_content_type,
                    owner_id=ad.id,
                    image=image_file,
                    type='Image'
                )

            messages.success(request, _("Ad Updated Successfully"), extra_tags='ClassifiedAd')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedAdList'))

        except Exception as e:
            messages.error(request, _(f"An error occurred during update: {e}"), extra_tags='ClassifiedAd')

    context = {
        'ad': ad,
        'ad_form': AdminClassifiedAdForm(instance=ad),
        'items': ad.items.all(),
        'attributes': ad.attributes.all(),
        'media_gallery': ClassifiedMedia.objects.filter(
            owner_model=ContentType.objects.get_for_model(ad),
            owner_id=ad.id
        )
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/ad/update.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedAdDelete(request, slug):
    # Use get_object_or_404 for better error handling
    ad = get_object_or_404(ClassifiedAd, slug=slug)

    if request.method == "POST":
        ad_title = ad.title  # Get the title before deleting
        ad.delete()

        # For an AJAX request, return a JSON response to confirm success
        return JsonResponse({'status': 'success', 'message': f'"{ad_title}" was deleted successfully.'})

    # This part is a fallback in case someone accesses the URL with a GET request
    context = {
        'item_to_delete': ad,
        'current_page': _('Classified Ads')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/ad/admin.html', context)

################# PromotedClassifiedAd Admin ########################
# Functions for managing Promoted Classified Ads

@authenticated_staff
@staff_only
def AdminPromotedClassifiedAdList(request):
    """
    Lists all promoted ads.
    """
    promoted_ads = PromotedClassifiedAd.objects.all()
    context = {
        'promoted_ads': promoted_ads,
        'current_page': _('Promoted Ads')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/promoted_ad/admin.html', context)


@authenticated_staff
@staff_only
def AdminPromotedClassifiedAdCreate(request):
    """
    Handles the creation of a new promoted ad.
    """
    promoted_ad_form = AdminPromotedClassifiedAdForm(request.POST or None)
    if request.method == "POST":
        if promoted_ad_form.is_valid():
            promoted_ad_form.save()
            messages.success(request, _("Promoted Ad Created Successfully"), extra_tags='PromotedAd')
            return HttpResponseRedirect(reverse_lazy('classified:AdminPromotedClassifiedAdList'))
        else:
            messages.error(request, _("Promoted Ad Not Created, Please Try Again"), extra_tags='PromotedAd')

    context = {
        'promoted_ad_form': promoted_ad_form,
        'current_page': _('Promoted Ads')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/promoted_ad/create.html', context)


@authenticated_staff
@staff_only
def AdminPromotedClassifiedAdUpdate(request, slug):
    """
    Updates an existing promoted ad.
    """
    promoted_ad = PromotedClassifiedAd.objects.get(slug=slug)
    promoted_ad_form = AdminPromotedClassifiedAdForm(request.POST or None, instance=promoted_ad)

    if request.method == "POST":
        if promoted_ad_form.is_valid():
            promoted_ad_form.save()
            messages.success(request, _("Promoted Ad Updated Successfully"), extra_tags='PromotedAd')
            return HttpResponseRedirect(reverse_lazy('classified:AdminPromotedClassifiedAdList'))
        else:
            messages.error(request, _("Promoted Ad Not Updated, Please Try Again"), extra_tags='PromotedAd')

    context = {
        'promoted_ad': promoted_ad,
        'promoted_ad_form': promoted_ad_form,
        'current_page': _('Promoted Ads')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/promoted_ad/update.html', context)


@authenticated_staff
@staff_only
def AdminPromotedClassifiedAdDelete(request, slug):
    """
    Deletes a promoted ad.
    """
    promoted_ad = PromotedClassifiedAd.objects.get(slug=slug)
    if request.method == "POST":
        promoted_ad.delete()
        messages.success(request, _("Promoted Ad Deleted Successfully"), extra_tags='PromotedAd')
        return HttpResponseRedirect(reverse_lazy('classified:AdminPromotedClassifiedAdList'))

    context = {
        'item_to_delete': promoted_ad,
        'current_page': _('Promoted Ads')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/promoted_ad/delete.html', context)




########################## ClassifiedReview Admin ################################

@authenticated_staff
@staff_only
def AdminClassifiedReviewList(request):
    reviews = ClassifiedReview.objects.all()
    context = {
        'reviews': reviews,
        'current_page': _('Reviews')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/review/admin.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedReviewUpdate(request, slug):
    review = ClassifiedReview.objects.get(slug=slug)
    review_form = AdminClassifiedReviewForm(request.POST or None, instance=review)

    if request.method == "POST":
        if review_form.is_valid():
            # Example: manually updating a status field
            instance = review_form.save(commit=False)
            instance.is_approved = request.POST.get('is_approved', False)
            instance.save()
            messages.success(request, _("Review Updated Successfully"), extra_tags='Review')
            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedReviewList'))
        else:
            messages.error(request, _("Review Not Updated, Please Try Again"), extra_tags='Review')

    context = {
        'review': review,
        'review_form': review_form,
        'current_page': _('Reviews')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/review/update.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedReviewDelete(request, slug):
    review = ClassifiedReview.objects.get(slug=slug)
    if request.method == "POST":
        review.delete()
        messages.success(request, _("Review Deleted Successfully"), extra_tags='Review')
        return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedReviewList'))

    context = {
        'item_to_delete': review,
        'current_page': _('Reviews')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/review/delete.html', context)

################# UserSearch Admin ########################
# Function for listing user searches

@authenticated_staff
@staff_only
def AdminUserSearchList(request):
    """
    Displays a list of all user searches.
    """
    user_searches = UserSearch.objects.all()
    context = {
        'user_searches': user_searches,
        'current_page': _('User Searches')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/user_search/admin.html', context)


################# UserSavedSearch Admin ########################
# Function for listing user saved searches

@authenticated_staff
@staff_only
def AdminUserSavedSearchList(request):
    """
    Displays a list of all user saved searches.
    """
    user_saved_searches = UserSavedSearch.objects.all()
    context = {
        'user_saved_searches': user_saved_searches,
        'current_page': _('User Saved Searches')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/user_saved_search/admin.html', context)

########################## Commercials Admin ################################



@authenticated_staff
@staff_only
def AdminCommercialsList(request):
    """
    Lists all commercials. The creation logic has been moved to AdminCommercialsCreate.
    """
    commercials = Commercials.objects.all()
    context = {
        'commercials': commercials,
        'current_page': _('Commercials')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/commercial/admin.html', context)


@authenticated_staff
@staff_only
def AdminCommercialsCreate(request):
    """
    Handles the creation of a new commercial.
    """
    commercial_form = AdminCommercialsForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if commercial_form.is_valid():
            commercial_form.save()
            messages.success(request, _("Commercial Added Successfully"), extra_tags='Commercial')
            return HttpResponseRedirect(reverse_lazy('classified:AdminCommercialsList'))
        else:
            messages.error(request, _("Commercial Not Added, Please Try Again"), extra_tags='Commercial')

    context = {
        'commercial_form': commercial_form,
        'current_page': _('Commercials')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/commercial/create.html', context)

# NOTE: The AdminCommercialsUpdate and AdminCommercialsDelete functions you already have are correct and do not need to be changed.


@authenticated_staff
@staff_only
def AdminCommercialsUpdate(request, slug):
    commercial = Commercials.objects.get(slug=slug)
    commercial_form = AdminCommercialsForm(request.POST or None, request.FILES or None, instance=commercial)

    if request.method == "POST":
        if commercial_form.is_valid():
            commercial_form.save()
            messages.success(request, _("Commercial Updated Successfully"), extra_tags='Commercial')
            return HttpResponseRedirect(reverse_lazy('classified:AdminCommercialsList'))
        else:
            messages.error(request, _("Commercial Not Updated, Please Try Again"), extra_tags='Commercial')

    context = {
        'commercial': commercial,
        'commercial_form': commercial_form,
        'current_page': _('Commercials')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/commercial/admin.html', context)


@authenticated_staff
@staff_only
def AdminCommercialsDelete(request, slug):
    commercial = Commercials.objects.get(slug=slug)
    if request.method == "POST":
        commercial.delete()
        messages.success(request, _("Commercial Deleted Successfully"), extra_tags='Commercial')
        return HttpResponseRedirect(reverse_lazy('classified:AdminCommercialsList'))

    context = {
        'item_to_delete': commercial,
        'current_page': _('Commercials')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/commercial/delete.html', context)