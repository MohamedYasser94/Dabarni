from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


from helper.commonHelper import *
from helper.decorators import *

# Assumption: Your models are in one of these locations. Adjust as needed.

User = get_user_model()


########################## Classified Category Admin ################################
# Note: These are the functions you provided as a reference.

@authenticated_staff
@staff_only
def AdminCustomerList(request):
    customer = User.objects.filter(access_level='Customer')


    context = {
        'customer': customer,

        'current_page': _('Customer')
    }
    return render(request, f'{BACKEND_TEMPLATES}/customer/customer/admin.html', context)


@authenticated_staff
@staff_only
def AdminCustomerUpdate(request, slug):
    customer = User.objects.get(slug=slug)
    if request.method == "POST":
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.is_active = True if request.POST.get('is_active') == 'on' else False
        customer.save()
        messages.success(request, _("Customer Updated Successfully"), extra_tags='Customer')
        return HttpResponseRedirect(reverse_lazy('customer:AdminCustomerList'))

    context = {
        'customer': customer,
        'current_page': _('Customer')
    }
    return render(request, f'{BACKEND_TEMPLATES}/customer/customer/edit.html', context)


@authenticated_staff
@staff_only
def AdminCustomerDelete(request, slug):
    customer = get_object_or_404(User, slug=slug)
    customer.delete()
    messages.success(request, _("Customer Deleted Successfully"), extra_tags='Customer')
    return HttpResponseRedirect(reverse_lazy('customer:AdminCustomerList'))


