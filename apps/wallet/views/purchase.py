
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.classified.models.job import *
from apps.wallet.models.billing import Purchase
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()


##########################      Blog Category Admin            ################################

@authenticated_staff
@staff_only
def AdminPurchaseTransaction(request):
    purchase = Purchase.objects.all().order_by('-id')


    context = {
        'purchase': purchase,
        'title': _('Purchase Transactions'),


    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/purchase/admin.html', context)

