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


# ------------------- Step 1: Choose User Type -------------------
def ChooseUserTypeView(request):
    """
    صفحة اختيار النوع (طالب خدمة / مقدم خدمة)
    """
    context = {
        'current_page': _('Choose User Type'),
    }
    return render(request, 'good/auth/choose_account_type.html', context)



# ------------------- Step 2: Register -------------------
def RegisterView(request):
    """
    صفحة الريجستر (هتكون فيها فورم التسجيل أو هنستدعي API بعدين)
    """
    context = {
        'current_page': _('Register'),
    }
    return render(request, 'good/auth/register.html', context)

# ------------------- Step 3: Confirm OTP -------------------
def ConfirmOTPView(request):
    """
    صفحة تأكيد OTP
    """
    context = {
        'current_page': _('Confirm OTP'),
    }
    return render(request, 'good/auth/confirm_otp.html', context) 


# ------------------- Step 4: Choose Location -------------------
def ChooseLocationView(request):
    """
    صفحة اختيار وتحديد الموقع (هيكون فيها خريطة أو اختيار Address)
    """
    context = {
        'current_page': _('Choose Location'),
    }
    return render(request, f'/auth/choose_location.html', context)

# ------------------- Client Home Page -------------------
def ClientHomeView(request):
    """
    صفحة الهوم بتاعت العميل (بعد ما يسجل ويدخل)
    """
    categories = JobCategories.objects.all()
    locations = UserAddress.objects.filter(user=request.user)
    context = {
        'current_page': _('Client Home'),
        'categories': categories,
        'locations': locations,
    }
    return render(request, 'good/client/home.html', context)

def my_jobs_view(request):
    """
    صفحة عرض الطلبات الخاصة بالمستخدم
    """
    context = {
        "current_page": _("طلباتي")
    }
    return render(request, "good/client/my_jobs.html", context)


def job_detail_page(request, job_id):
    """
    صفحة تفاصيل الطلب (البيانات بتيجي من API بالـ JavaScript)
    """
    context = {
        "current_page": _("تفاصيل الطلب"),
        "job_id": job_id
    }
    return render(request, "good/client/job_detail.html", context)

# ------------------- Provider Home Page -------------------
def ProviderHomeView(request):
    """
    صفحة الهوم بتاعت مقدم الخدمة (بعد ما يسجل ويدخل)
    """
    context = {
        'current_page': _('Provider Home'),
    }

    return render(request, 'good/provider/home.html', context)



def renderProviderJobDetailsPage(request, job_id):
    """
    View to render the provider's job details page.
    """
    context = {
        'current_page': _('Job Details'),
        'job_id': job_id,
    }
    return render(request, 'good/provider/job_details.html', context)



def renderCustomerJobOffersPage(request, job_id):
    """
    View to render the customer's job offers page.
    """
    context = {
        'current_page': _('Job Offers'),
        'job_id': job_id,
    }
    print("TETS")
    return render(request, 'good/client/job_offers.html', context)





