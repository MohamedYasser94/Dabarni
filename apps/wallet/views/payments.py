from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

from apps.wallet.forms.payment import AdminPaymentGatewayForm
from apps.wallet.models.payment import PaymentGateway, PaymentGatewaySetting
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, authenticated_staff


@authenticated_staff
@superuser_only
def AdminPaymentGatewayList(request):
    gateway = PaymentGateway.objects.all()
    gateway_form = AdminPaymentGatewayForm(request.POST or None)


    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        setting_key = request.POST.get('setting_key')
        setting_secret = request.POST.get('setting_secret')


        if name :
            try:
                gateway_object = PaymentGateway.objects.get(name=name,)
                gateway_name = gateway_object.name


                if image:
                    gateway_object.image = image
                else:
                    gateway_object.image = gateway_object.image
                gateway_object.save()

                setting__object = PaymentGatewaySetting.objects.get(gateway=gateway_object)
                setting__object.setting_key = setting_key
                setting__object.setting_secret = setting_secret
                setting__object.save()


            except Exception as e:
                gateway_object = PaymentGateway(
                    name=name,
                    gateway_name = name,
                    image=image,
                )
                gateway_object.save()
                setting__object = PaymentGatewaySetting(
                    gateway=gateway_object,
                    setting_key=setting_key,
                    setting_secret=setting_secret
                )
                setting__object.save()
            messages.success(request, _('Payment Gateway Added Successfully'),extra_tags='PaymentGateway')
        else:
            messages.error(request, _('Please fill all the fields'),extra_tags='PaymentGateway')

    context = {
        'gateway': gateway,
        'gateway_form': gateway_form,
        'title': _('Payment Gateway'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/payment/payments/admin.html', context)


@authenticated_staff
@superuser_only
def AdminPaymentGatewayUpdate(request, slug):
    gateway = PaymentGateway.objects.get(slug=slug)
    gateway_form = AdminPaymentGatewayForm(request.POST or None, instance=gateway)

    if request.method == 'POST':
        if gateway_form:
            name = request.POST.get('name')
            image = request.FILES.get('image')
            setting_key = request.POST.get('setting_key')
            setting_secret = request.POST.get('setting_secret')

            gateway_object = PaymentGateway.objects.get(slug=slug)
            gateway_object.name = name
            gateway_object.gateway_name = name
            if image:
                gateway_object.image = image
            else:
                gateway_object.image = gateway_object.image
            gateway_object.save()
            try:
                setting_object = PaymentGatewaySetting.objects.get(gateway=gateway_object)
                setting_object.setting_key = setting_key
                setting_object.setting_secret = setting_secret
                setting_object.save()
            except PaymentGatewaySetting.DoesNotExist:
                setting_object = PaymentGatewaySetting(
                    gateway=gateway_object,
                    setting_key=setting_key,
                    setting_secret=setting_secret
                )
                setting_object.save()
            messages.success(request, _('Payment Gateway Updated Successfully'), extra_tags='PaymentGateway')
            return redirect('wallet:AdminPaymentGatewayList')
        else:
            messages.error(request, _('Please fill all the fields'), extra_tags='PaymentGateway')

    context = {
        'gateway': gateway,
        'gateway_form': gateway_form,
        'title': _('Payment Gateway'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/payment/payments/update.html', context)

@authenticated_staff
@superuser_only
def AdminPaymentGatewayDelete(request, slug):
    gateway = PaymentGateway.objects.get(slug=slug)
    gateway.delete()
    messages.success(request, _('Payment Gateway Deleted Successfully'), extra_tags='PaymentGateway')
    return redirect('shop:AdminPaymentGatewayList')












