from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from datetime import datetime

from django.db.models import Prefetch

from apps.classified.models.models import Job, JobProgress, JobOffer, JobNegotiate
from helper.commonHelper import *
from helper.decorators import *
from user.models import UserAddress, UserProfile
from api.v1.constants import JobProgressStatus

# Assumption: Your models are in one of these locations. Adjust as needed.

User = get_user_model()


########################## Classified Category Admin ################################
# Note: These are the functions you provided as a reference.

@authenticated_staff
@staff_only
def AdminCustomerList(request):
    customers = User.objects.filter(access_level='Client').order_by('-id')


    context = {
        'customers': customers,
        'current_page': 'العملاء'
    }
    return render(request, f'{BACKEND_TEMPLATES}/customer/customer/admin.html', context)

@authenticated_staff
@staff_only
def AdminCustomerUpdate(request, slug):
    customer = get_object_or_404(User, slug=slug)

    # اجلب profile و address بأمان (filter().first() ما بترميش استثناء)
    profile = UserProfile.objects.filter(user=customer).first()
    address = UserAddress.objects.filter(user=customer, default='Active').first()

    if request.method == "POST":
        try:
            with transaction.atomic():
                customer.first_name = request.POST.get('first_name', '').strip() or None
                customer.last_name = request.POST.get('last_name', '').strip() or None
                customer.email = request.POST.get('email', '').strip() or None
                customer.phone = request.POST.get('phone', '').strip() or None
                customer.image = request.FILES.get('image') or customer.image



                # Account status from select
                is_active_val = (request.POST.get('is_active') or '').strip()
                customer.is_active = 'Active' if is_active_val == 'Active' else 'Inactive'
                customer.save()

                if not profile:
                    profile = UserProfile.objects.create(user=customer)

                # Is citizen from select (truthy values -> True)
                is_citizen_val = (request.POST.get('is_citizen') or '').strip().lower()
                profile.is_citizen = is_citizen_val in ('1', 'true', 'yes', 'on', 'active')

                # Read DOB from 'dob' (matches template)
                dob_str = (request.POST.get('dob') or '').strip()
                if dob_str:
                    try:
                        profile.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                    except ValueError:
                        profile.dob = None
                else:
                    profile.dob = None

                if request.FILES.get('id_image_front'):
                    profile.id_image_front = request.FILES['id_image_front']
                if request.FILES.get('id_image_back'):
                    profile.id_image_back = request.FILES['id_image_back']
                if request.FILES.get('residence_image'):
                    profile.residence_image = request.FILES['residence_image']

                profile.save()

                if not address:
                    address = UserAddress.objects.create(user=customer, default='Active')

                address.address = request.POST.get('address', '').strip() or None
                address.save()

            messages.success(request, "Customer Updated Successfully", extra_tags='Customer')
            return HttpResponseRedirect(reverse_lazy('customer:AdminCustomerList'))

        except Exception as e:
            messages.error(request, f"Error updating customer: {str(e)}", extra_tags='Customer')

    context = {
        'customer': customer,
        'profile': profile,
        'address': address,
        'current_page': 'تعديل عميل',
    }
    return render(request, f'{BACKEND_TEMPLATES}/customer/customer/update.html', context)

@authenticated_staff
@staff_only
def AdminCustomerDelete(request, slug):
    customer = get_object_or_404(User, slug=slug)
    customer.is_active = 'Archived' # Soft delete logic
    customer.save()
    messages.success(request, "Customer Deleted Successfully", extra_tags='Customer')
    return HttpResponseRedirect(reverse_lazy('customer:AdminCustomerList'))


########################## Customer Jobs Admin ################################
@authenticated_staff
@staff_only
def AdminCustomerJobList(request,slug):
    user = get_object_or_404(User, slug=slug)

    # Base prefetch: latest negotiations for this customer per job, ordered desc
    negotiations_prefetch = Prefetch(
        'job__negotiates',
        queryset=JobNegotiate.objects.filter(customer=user).order_by('-id'),
        to_attr='negotiations_ordered'
    )

    base_qs = (
        JobProgress.objects
        .filter(customer=user)
        .select_related('job__category', 'provider__user', 'offer')
        .prefetch_related(negotiations_prefetch)
        .order_by('-id')
    )

    pending_progresses = base_qs.filter(progress_status=JobProgressStatus.PENDING)
    in_progress_progresses = base_qs.filter(progress_status=JobProgressStatus.IN_PROGRESS)
    completed_progresses = base_qs.filter(progress_status=JobProgressStatus.COMPLETED)
    cancelled_progresses = base_qs.filter(progress_status=JobProgressStatus.CANCELLED)

    context = {
        'customer': user,
        'pending_progresses': pending_progresses,
        'in_progress_progresses': in_progress_progresses,
        'completed_progresses': completed_progresses,
        'cancelled_progresses': cancelled_progresses,
        'current_page': 'وظائف العملاء'
    }
    return render(request, f'{BACKEND_TEMPLATES}/customer/job/admin.html', context)
