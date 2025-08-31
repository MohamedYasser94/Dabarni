from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.classified.models.models import *
from apps.wallet.models.billing import Purchase
from apps.wallet.models.points import PointSetting
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()


##########################      Blog Category Admin            ################################

@authenticated_staff
@staff_only
def AdminPointSetting(request):
    setting = PointSetting.objects.all()


    if request.method == 'POST':
        money_spent_for_one_point = request.POST.get('money_spent_for_one_point')
        point_value_in_money = request.POST.get('point_value_in_money')
        points_expire_in_days = request.POST.get('points_expire_in_days')
        min_purchase_to_earn = request.POST.get('min_purchase_to_earn')
        try:
            setting_object = PointSetting.objects.get(id=setting[0].id)
            setting_object.money_spent_for_one_point = money_spent_for_one_point
            setting_object.point_value_in_money = point_value_in_money
            setting_object.points_expire_in_days = points_expire_in_days
            setting_object.min_purchase_to_earn = min_purchase_to_earn
            setting_object.save()
        except:
            setting_object = PointSetting.objects.create(
                money_spent_for_one_point=money_spent_for_one_point,
                point_value_in_money=point_value_in_money,
                points_expire_in_days=points_expire_in_days,
                min_purchase_to_earn=min_purchase_to_earn
            )
            setting_object.save()
        msg = _('Settings updated successfully.')
        messages.success(request, msg,extra_tags='PointSetting')
        return redirect('wallet:AdminPointSetting')

    context = {
        'setting': setting,
        'title': _('Points Settings'),


    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/point_setting/admin.html', context)



@authenticated_staff
@staff_only
def AdminPointSettingUpdate(request,slug):
    setting = PointSetting.objects.get(slug=slug)


    if request.method == 'POST':
        money_spent_for_one_point = request.POST.get('money_spent_for_one_point')
        point_value_in_money = request.POST.get('point_value_in_money')
        points_expire_in_days = request.POST.get('points_expire_in_days')
        min_purchase_to_earn = request.POST.get('min_purchase_to_earn')

        setting.money_spent_for_one_point = money_spent_for_one_point
        setting.point_value_in_money = point_value_in_money
        setting.points_expire_in_days = points_expire_in_days
        setting.min_purchase_to_earn = min_purchase_to_earn
        setting.save()

        msg = _('Settings updated successfully.')
        messages.success(request, msg,extra_tags='PointSetting')
        return redirect('wallet:AdminPointSetting')

    context = {
        'setting': setting,
        'title': _('Points Settings'),


    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/point_setting/update.html', context)

@authenticated_staff
@staff_only
def AdminPointSettingDelete(request,slug):
    setting = PointSetting.objects.get(id=slug)
    setting.delete()
    msg = _('Settings deleted successfully.')
    messages.success(request, msg,extra_tags='PointSetting')
    return redirect('wallet:AdminPointSetting')
