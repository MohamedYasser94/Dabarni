from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.classified.models.models import *
from apps.provider.forms.forms import AdminJobProviderForm
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()




##########  JobProvider  Admin #########
@authenticated_staff
@staff_only
def AdminProviderList(request):
    providers = JobProvider.objects.all()
    context = {
        'providers': providers,
        'current_page': _('Providers')
    }
    return render(request, f'{BACKEND_TEMPLATES}/provider/provider/admin.html', context)


@authenticated_staff
@staff_only
def AdminProviderDetails(request, slug):
    provider = JobProvider.objects.get(slug=slug)

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
    provider = JobProvider.objects.get(slug=slug)

    if request.method == "POST":
        provider_form = AdminJobProviderForm(request.POST or None, request.FILES or None)

        if provider_form:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            type = request.POST.get('type')
            description = request.POST.get('description')
            id_image = request.FILES.get('id_image')
            document_image = request.FILES.get('document_image')
            proof_image = request.FILES.get('proof_image')
            location_image = request.FILES.get('location_image')
            image = request.FILES.get('image')
            number = request.POST.get('number')
            proof_number = request.POST.get('proof_number')
            id_number = request.POST.get('id_number')
            document_number = request.POST.get('document_number')
            bank_account = request.POST.get('bank_account')
            governorate = request.POST.get('governorate')
            address = request.POST.get('address')
            website = request.POST.get('website')
            data_confirmed = request.POST.get('data_confirmed')
            status = request.POST.get('status')

            provider_object = JobProvider.objects.get(id=provider.id)
            provider_object.name = name
            provider_object.email = email
            provider_object.phone = phone
            provider_object.type = type
            provider_object.description = description
            if id_image:
                provider_object.id_image = id_image
            if document_image:
                provider_object.document_image = document_image
            if proof_image:
                provider_object.proof_image = proof_image
            if location_image:
                provider_object.location_image = location_image
            if image:
                provider_object.image = image
            provider_object.number = number
            provider_object.proof_number = proof_number
            provider_object.id_number = id_number
            provider_object.document_number = document_number
            provider_object.bank_account = bank_account
            if governorate == '' or governorate == "''" or governorate == None:
                provider_object.governorate_id = None
            else:
                provider_object.governorate_id = governorate
            provider_object.address = address
            provider_object.website = website
            provider_object.data_confirmed = data_confirmed
            provider_object.status = status
            provider_object.save()
            messages.success(request, _("Provider Update Successfully"), extra_tags='Provider')
            return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))
        else:
            messages.error(request, _("Provider Not Update , Please Try Again"), extra_tags='Provider')

    context = {
        'provider': provider,
        'provider_form': AdminJobProviderForm(),
        'current_page': _('Update Provider'),
        'prev_Page': _('Providers'),
        'prev_Page_link': reverse_lazy('provider:AdminProviderList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/provider/provider/update.html', context)


@authenticated_staff
@staff_only
def AdminProviderDelete(request, slug):
    provider = JobProvider.objects.get(slug=slug)
    if request.method == "POST":
        provider.delete()
        messages.success(request, _("Provider Delete Successfully"), extra_tags='Provider')
        return HttpResponseRedirect(reverse_lazy('provider:AdminProviderList'))






