from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from apps.classified.models.models import *
from apps.provider.forms.forms import AdminJobProviderForm
from helper.commonHelper import *
from helper.decorators import *
from django.db.models import Prefetch
User = get_user_model()



@authenticated_staff
@staff_only
def AdminProviderList(request):
    providers = (
        JobProvider.objects
        .select_related("user", "category") 
        # .prefetch_related("user__addresses") # Corrected: use prefetch_related for the reverse relationship
        .all()
        .order_by("-id")
    )

    context = {
        "providers": providers,
        "current_page": _("Providers"),
    }
    return render(request, f"{BACKEND_TEMPLATES}/provider/provider/admin.html", context)

@authenticated_staff
@staff_only
def AdminProviderDetails(request, slug):
    provider = get_object_or_404(JobProvider.objects.select_related('user', 'category'), slug=slug)

    context = {
        'provider': provider,
        'current_page': _('Provider Details'),
        'prev_Page': _('Providers'),
        'prev_Page_link': reverse_lazy('provider:AdminProviderList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/provider/provider/details.html', context)

@authenticated_staff
@staff_only
def AdminProviderUpdate(request, slug):
    provider = get_object_or_404(JobProvider.objects.select_related('user', 'category'), slug=slug)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Manually get and update fields from User model
                user = provider.user
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.email = request.POST.get('email', user.email)
                user.phone = request.POST.get('phone', user.phone)
                user.is_active = 'Active' if request.POST.get('is_active') == 'on' else 'Inactive'
                user.save()

                # Manually get and update fields from JobProvider model
                provider.category_id = request.POST.get('category', provider.category_id)
                provider.experience_years = request.POST.get('experience_years', provider.experience_years)
                provider.company = request.POST.get('company', provider.company)
                provider.bio = request.POST.get('bio', provider.bio)
                provider.address = request.POST.get('address', provider.address)
                provider.commercial_number = request.POST.get('commercial_number', provider.commercial_number)
                provider.vat_number = request.POST.get('vat_number', provider.vat_number)
                provider.license_number = request.POST.get('license_number', provider.license_number)
                provider.bank_account = request.POST.get('bank_account', provider.bank_account)
                provider.data_confirmed = request.POST.get('data_confirmed', provider.data_confirmed)
                provider.status = request.POST.get('status', provider.status)
                
                # Handle file uploads
                if request.FILES.get('commercial_image'):
                    provider.commercial_image = request.FILES.get('commercial_image')
                if request.FILES.get('commercial_image2'):
                    provider.commercial_image2 = request.FILES.get('commercial_image2')
                if request.FILES.get('vat_image'):
                    provider.vat_image = request.FILES.get('vat_image')
                if request.FILES.get('license_image'):
                    provider.license_image = request.FILES.get('license_image')

                provider.save()

            messages.success(request, _("Provider Updated Successfully"), extra_tags='Provider')
            return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))

        except Exception as e:
            messages.error(request, f"Error updating provider: {str(e)}", extra_tags='Provider')
            
    context = {
        'provider': provider,
        'categories': JobCategories.objects.all(),
        'current_page': _('Update Provider'),
        'prev_Page': _('Providers'),
        'prev_Page_link': reverse_lazy('provider:AdminProviderList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/provider/provider/update.html', context)

@authenticated_staff
@staff_only
def AdminProviderDelete(request, slug):
    provider = get_object_or_404(JobProvider, slug=slug)
    
    if request.method == "POST":
        provider.status = 'Archived' # Perform the soft delete
        provider.save()

        messages.success(request, _("Provider Deleted Successfully"), extra_tags='Provider')
        return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))

    # If it's a GET request, you might want to show a confirmation page
    context = {
        'provider': provider,
        'current_page': _('Delete Provider'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/provider/provider/confirm_delete.html', context)

@authenticated_staff
@staff_only
def AdminProviderCreate(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                password = request.POST.get('password')
                category_id = request.POST.get('category_id')

                if not all([first_name, last_name, email, phone, password, category_id]):
                    messages.error(request, _("All required fields must be filled."), extra_tags='Provider')
                    return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))
                
                # Create the User first
                user = User.objects.create_user(email=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone
                user.access_level = 'Provider'
                user.is_active = 'Active' # Admin can activate directly
                user.save()
                
                # Create the JobProvider profile
                category = get_object_or_404(JobCategories, pk=category_id)
                JobProvider.objects.create(
                    user=user,
                    category=category,
                    business_phone=phone,
                    data_confirmed='Yes' # Admin confirms directly
                )
            
            messages.success(request, _("Provider created successfully."), extra_tags='Provider')
            return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))

        except Exception as e:
            messages.error(request, f"Error creating provider: {str(e)}", extra_tags='Provider')
            return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))
            
    return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))




