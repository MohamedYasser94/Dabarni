from datetime import datetime

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.classified.views.utils import FrontIndexClassifiedAppData
from apps.front.views.utils import *

from core.models.core import *

from helper.commonHelper import *


# Create your views here.


def HomeIndex(request):
    system_app = SystemSetting.objects.get(title='Digithup')
    if system_app.maintenance == 'Active':
        front_data = FrontIndexFrontAppData(request)
        context = {

            'front_data': front_data,

            'current_page': 'Home',
        }
        return render(request,  f'frontend/{MAINTENANCE_TEMPLATES}/index.html',context )
    elif system_app.maintenance == 'Inactive':


        front_data = FrontIndexFrontAppData(request)
        classified_data = FrontIndexClassifiedAppData(request)


        context = {

            'front_data': front_data,
            'classified_data': classified_data,
            'current_page': 'Home',
        }
        return render(request,  f'frontend/{ACTIVE_FRONTEND_TEMPLATES}/index.html',context )








def FAQ(request):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/contact/faq.html', )

def FrontPrivacyPolicy(request):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/contact/privacypolicy.html', )

def FrontTermsOfService(request):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/contact/termsofservice.html', )


def FrontRequestAQuote(request):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/contact/request-a-quote.html', )
def FrontTermsConditions(request):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/contact/termsconditions.html', )




def server_error_view(request, template_name=f'{ACTIVE_FRONTEND_TEMPLATES}/error/500.html'):
    return render(request,
                  template_name,
                  {'message': '哎呀，出错了，我已经收集到了错误信息，之后会抓紧抢修，请点击首页看看别的？',
                   'statuscode': '500'},
                  status=500)





def page_not_found_view(request, exception):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/error/404.html', status=404)


def error403(request, ):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/error/403.html', status=403)


def error404(request, exception):
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/error/404.html', status=404)




def comming_soon(request):
    return render(request, 'front/ErrorPage/comming-soon.html', )


def FrontTestPage(request):
    confirm_message = _(f'Dear, Hitham Gamal Mohamed \n'
                        f'We have received your request for registration in  Expontion event  \n'
                        f'and will send you an email once your registration is confirmed. \n'

                        f'”Thank you for your interest.”')
    message = confirm_message
    context = {'message': message,

               }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/email/ticket/request.html',context )
