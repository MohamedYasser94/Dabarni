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
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone # عدل المسار لو لازم
from apps.wallet.models.models import Wallet, WalletMoney

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


def renderCustomerPaymentSummary(request, offer_id):
    # تأكد إن المستخدم مسجل دخول
    if not request.user.is_authenticated:
        return redirect('login')  # أو ارجع 403 حسب رغبتك

    # جلب العرض والتأكد إنه يخص ال customer (عبر job.customer)
    qs = JobOffer.objects.select_related("job__customer", "provider__user")

    if not request.user.is_superuser:
        qs = qs.filter(job__customer=request.user)

    offer = get_object_or_404(qs, pk=offer_id)


    # السعر (احتمال يكون None) — استخدم Decimal
    price = offer.price if offer.price is not None else Decimal('0.00')
    if not isinstance(price, Decimal):
        try:
            price = Decimal(str(price))
        except (InvalidOperation, TypeError):
            price = Decimal('0.00')

    tax = Decimal('2.00')
    total = price + tax

    # الوقت المعروض: أولوية scheduled_at (job) ثم offer.create_at ثم الآن
    payment_time = getattr(offer.job, 'scheduled_at', None) or offer.create_at or timezone.now()
    payment_time_local = timezone.localtime(payment_time)

    # اسم العميل
    # provider object (مش QuerySet)
    provider = get_object_or_404(JobProvider, id=offer.provider.id)

    # جلب اسم الـ provider من user المرتبط
    if provider.user.get_full_name():
        provider_name = provider.user.get_full_name()
    else:
        provider_name = provider.user.username or (
            f"{provider.user.first_name} {provider.user.last_name}".strip()
        ) or "غير معروف"


    context = {
        "offer": offer,
        "payment_time": payment_time_local,
        "provider_name": provider_name,
        "reference_id": offer.code or f"REF-{offer.id}",
        "amount": price,
        "tax": tax,
        "total": total,
    }

    return render(request, "good/client/payment_summary.html", context)

#----------------------------------------
def renderConfirmPayment(request, offer_id):
    """
    GET: عرض صفحة تأكيد الدفع فقط.
    لاحظ: لا تقم بأي منطق خاص بالمحفظة هنا — سيتم تنفيذ الدفع عبر JS + API endpoints.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    offer = get_object_or_404(
        JobOffer.objects.select_related('job__customer', 'job', 'provider__user'),
        pk=offer_id
    )

    # حساب السعر والضريبة والمجموع لعرضها في القالب
    try:
        price = Decimal(str(offer.price)) if offer.price is not None else Decimal("0.00")
    except (InvalidOperation, TypeError):
        price = Decimal("0.00")
    tax = Decimal("2.00")
    total = price + tax

    # جلب progress إن وجد للعرض (للاستعراض فقط)
    progress = JobProgress.objects.filter(offer=offer).first()

    # جلب المحفظة للعرض (ليس للاجراء) — هذا يبقى للـ frontend الاستهلاك من الـ API، لكن العرض مفيد
    wallet = Wallet.objects.filter(user_id=request.user.id).select_related("wallet_locked").first()
    wallet_money = WalletMoney.objects.filter(wallet=wallet, user=request.user).first() if wallet else None

    context = {
        "offer": offer,
        "price": price,
        "tax": tax,
        "total": total,
        "wallet": wallet,               # مجرد معلومات للعرض إن رغبت
        "wallet_money": wallet_money,   # مجرد معلومات للعرض إن رغبت
        "provider_name": (offer.provider.company or offer.provider.user.get_full_name()) if getattr(offer, "provider", None) else "مزود غير معروف",
        "reference_id": offer.code or f"REF-{offer.id}",
        "progress": progress,
        # ضروري: نرسل بعض الأشياء للـ JS لبناء روابط الـ API/Redirect بشكل آمن
        "offer_id": offer.id,
        "job_id": getattr(offer.job, "id", ""),
    }
    return render(request, "good/client/confirm_payment.html", context)



def renderJobProgress(request, progress_id):
    progress = get_object_or_404(
        JobProgress.objects.select_related(
            "job__category",  
            "offer",
            "provider__user"
        ),
        pk=progress_id
    )
    job = progress.job 
    context = {
        "progress": progress,
        "job": job,
        "job_id": job.id,  
        "category": job.category,  
        "offer": getattr(progress, 'offer', None),
        "provider": getattr(progress, 'provider', None),
        "customer": getattr(progress, 'customer', None),
        "progress_id": progress.id,  # ✅ ضيفنا progress_id هنا
    }
    return render(request, "good/client/job_progress.html", context)




def help_page(request):
    """
    صفحة طلب المساعدة - FAQ + التواصل مع خدمة العملاء
    """
    context = {
        "current_page": _("طلب المساعدة"),
    }
    return render(request, "good/help_page.html", context)


def rate_provider_page(request, job_id):
    """
    Render a page where the customer can rate the provider for a completed job.
    """
    context = {
        'job_id': job_id
    }
    return render(request, 'good/client/rate_provider.html', context)



def rate_customer_page(request, job_id):
    """
    Render a page where the provider can rate the customer for a completed job.
    """
    context = {
        'job_id': job_id
    }
    return render(request, 'good/provider/rate_client.html', context)
