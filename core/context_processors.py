import os
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models import Sum
from core.models.core import SystemSetting, SiteSetting, CommonMediaFiles, CommonSeo
from core.models.localization import Language
from core.models.notifications import Notification


User = get_user_model()


def setting_processors(request):
    try:
        system_setting_add = SystemSetting.objects.filter(status='Active')
    except Exception as e:
        system_setting_add = SystemSetting.objects.create(title='Digithup')
    system_info_add = SiteSetting.objects.get_or_create(title='Digithup')
    system_settings = SystemSetting.objects.filter(status='Active').last()
    dashboard_setting = SiteSetting.objects.filter(status='Active').last()
    dashboard_setting.domain = request._current_scheme_host
    dashboard_setting.save()
    sites = Site.objects.all()
    for site in sites:
        site.domain = request._current_scheme_host
        site.name = 'Digithup'
        site.save()

    try:
        dashboard_image = CommonMediaFiles.objects.filter(type='hero',
                                                          owner_model=ContentType.objects.get(model='SiteSetting'),
                                                          owner_id=dashboard_setting.id)
        dashboard_seo = CommonSeo.objects.filter(owner_model=ContentType.objects.get(model='SiteSetting'),
                                                 owner_id=dashboard_setting.id)
        dashboard_app = SystemSetting.objects.get(title='Digithup').app

        return {
            'dashboard_setting': dashboard_setting,
            'dashboard_image': dashboard_image,
            'dashboard_seo': dashboard_seo,
            'system_settings': system_settings,
            'dashboard_app': dashboard_app,

        }
    except BaseException as e:

        return {
            'dashboard_setting': None,
            'dashboard_image': None,
            'dashboard_seo': None,
            'dashboard_app': None,
            'system_settings': system_settings,

        }


def geoip_processors(request):
    try:

        import IP2Location
        database = IP2Location.IP2Location(os.path.join("helper/geoip/IP2LOCATION-LITE-DB11.BIN"))

        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        if ip == '127.0.0.1':  # Only define the IP if you are testing on localhost.
            ip = '127.0.0.1'

        device_type = ""
        browser_type = ""
        browser_version = ""
        os_type = ""
        os_version = ""
        if request.user_agent.is_mobile:
            device_type = "Mobile"
        if request.user_agent.is_tablet:
            device_type = "Tablet"
        if request.user_agent.is_pc:
            device_type = "PC"

        browser_type = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version_string
        os_type = request.user_agent.os.family
        os_version = request.user_agent.os.version_string

        location = database.get_all(ip)
        location_country = database.get_country_short(ip)
        country_name = database.get_country_long(ip)

        location_city = database.get_city(ip)
        location_region = database.get_region(ip)
        location_latitude = database.get_latitude(ip)
        location_longitude = database.get_longitude(ip)
        location_zipcode = database.get_zipcode(ip)
        location_timezone = database.get_timezone(ip)
        location_isp = database.get_isp(ip)
        location_domain = database.get_domain(ip)


        return {
            'location': location,
            "ip": ip,
            "device_type": device_type,
            "browser_type": browser_type,
            "browser_version": browser_version,
            "os_type": os_type,
            "os_version": os_version,
            "location_country": location_country,
            'country_name': country_name,
            "location_city": location_city,
            "location_region": location_region,
            "location_latitude": location_latitude,
            "location_longitude": location_longitude,
            "location_zipcode": location_zipcode,
            "location_timezone": location_timezone,
            "location_isp": location_isp,
            "location_domain": location_domain

        }

    except Exception as e:

        return {
            'geoipError': e,
            "ip": None,
            "device_type": None,
            "browser_type": None,
            "browser_version": None,
            "os_type": None,
            "os_version": None,
            "location_country": None,
            "location_city": None
        }


def language_processors(request):
    language = Language.objects.all()


    try:
        en_language = Language.objects.get(name='en', code='en', default='Inactive')
        return {
            'current_lang': request.LANGUAGE_CODE,
            'available_lang': list(language.values('id', 'code', 'name')),
            'en_language': language.get(name='en'),
            'ar_language': language.get(name='ar'),
        }

    except Exception as e:

        return {
            'current_lang':request.LANGUAGE_CODE,
            'en_language': 'en',
            'ar_language':  'ar',
        }





def template_processors(request):
    try:
        system_check = SystemSetting.objects.get_or_create(title='Digithup')
        system_setting = SystemSetting.objects.get(title='Digithup')
        if system_setting.maintenance == 'Active':
            if not request.user.is_authenticated:
                return {

                'TEMPLATES_BACKEND': SystemSetting.objects.get(title='Digithup').backend_temp,
                'BACKEND_ASSETS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/assets',
                'BACKEND_BASE': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/adminbase.html',
                'BACKEND_HEAD': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/head.html',
                'BACKEND_HEADER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/header.html',
                'BACKEND_SLIDER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/slider.html',
                'BACKEND_SIDEBAR': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/sidebar.html',
                'BACKEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/common/breadcrumb.html',
                'BACKEND_BODY': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/content.html',
                'BACKEND_FOOTER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/footer.html',
                'BACKEND_DRAWER': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/drawer.html',
                'BACKEND_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/js.html',
                'BACKEND_VUE_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/vuejs.html',

                ############################ Frontend #########################################
                'FRONTEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').maintenance_temp,
                'FRONTEND_INDEX': SystemSetting.objects.get(title='Digithup').frontend_temp,
                'FRONTEND_ASSETS': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/assets',
                'FRONTEND_BASE': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/homebase.html',
                'FRONTEND_HEAD': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/head.html',
                'FRONTEND_HEADER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/header.html',
                'FRONTEND_SLIDER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/slider.html',
                'FRONTEND_PLAYER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/player.html',
                'FRONTEND_VUE': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/vuejs.html',
                'FRONTEND_SIDEBAR': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/sidebar.html',
                'FRONTEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/common/breadcrumb.html',
                'FRONTEND_BODY': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/content.html',
                'FRONTEND_FOOTER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/footer.html',
                'FRONTEND_MODAL': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').maintenance_temp + '/modal.html',
                'FRONTEND_JS': 'frontend/' + SystemSetting.objects.get(title='Digithup').maintenance_temp + '/js.html',

            }
            else:
                return {

                    'TEMPLATES_BACKEND': SystemSetting.objects.get(title='Digithup').backend_temp,

                    'BACKEND_ASSETS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/assets',
                    'BACKEND_BASE': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/adminbase.html',
                    'BACKEND_HEAD': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/head.html',
                    'BACKEND_HEADER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/header.html',
                    'BACKEND_SLIDER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/slider.html',
                    'BACKEND_SIDEBAR': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/sidebar.html',
                    'BACKEND_BREADCRUMB': SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/common/breadcrumb.html',
                    'BACKEND_BODY': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/content.html',
                    'BACKEND_FOOTER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/footer.html',
                    'BACKEND_DRAWER': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/drawer.html',
                    'BACKEND_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/js.html',
                    'BACKEND_VUE_JS': 'backend/' + SystemSetting.objects.get(
                        title='Digithup').backend_temp + '/vuejs.html',

                    'FRONTEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').frontend_temp,
                    'FRONTEND_ASSETS': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/assets',
                    'FRONTEND_BASE': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/homebase.html',
                    'FRONTEND_HEAD': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/head.html',
                    'FRONTEND_HEADER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/header.html',
                    'FRONTEND_SLIDER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/slider.html',
                    'FRONTEND_PLAYER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/player.html',
                    'FRONTEND_VUE': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/vuejs.html',
                    'FRONTEND_SIDEBAR': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/sidebar.html',
                    'FRONTEND_BREADCRUMB': SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/common/breadcrumb.html',
                    'FRONTEND_BODY': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').maintenance_temp + '/content.html',
                    'FRONTEND_FOOTER': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/footer.html',
                    'FRONTEND_MODAL': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/modal.html',
                    'FRONTEND_JS': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/js.html',

                }
        else:
            return {

                'TEMPLATES_BACKEND': SystemSetting.objects.get(title='Digithup').backend_temp,

                'BACKEND_ASSETS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/assets',
                'BACKEND_BASE': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/adminbase.html',
                'BACKEND_HEAD': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/head.html',
                'BACKEND_HEADER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/header.html',
                'BACKEND_SLIDER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/slider.html',
                'BACKEND_SIDEBAR': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/sidebar.html',
                'BACKEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/common/breadcrumb.html',
                'BACKEND_BODY': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/content.html',
                'BACKEND_FOOTER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/footer.html',
                'BACKEND_DRAWER': 'backend/' + SystemSetting.objects.get(
                    title='Digithup').backend_temp + '/drawer.html',
                'BACKEND_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/js.html',
                'BACKEND_VUE_JS': 'backend/' + SystemSetting.objects.get(title='Digithup').backend_temp + '/vuejs.html',

                'FRONTEND_TEMPLATES': SystemSetting.objects.get(title='Digithup').frontend_temp,
                'FRONTEND_ASSETS': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/assets',
                'FRONTEND_BASE': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/homebase.html',
                'FRONTEND_HEAD': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/head.html',
                'FRONTEND_HEADER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/header.html',
                'FRONTEND_SLIDER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/slider.html',
                'FRONTEND_PLAYER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/player.html',
                'FRONTEND_VUE': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/vuejs.html',
                'FRONTEND_SIDEBAR': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/sidebar.html',
                'FRONTEND_BREADCRUMB': SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/common/breadcrumb.html',
                'FRONTEND_BODY': 'frontend/' + SystemSetting.objects.get(
                        title='Digithup').frontend_temp + '/' + SystemSetting.objects.get(
                        title='Digithup').home_index+'.html',
                'FRONTEND_FOOTER': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/footer.html',
                'FRONTEND_MODAL': 'frontend/' + SystemSetting.objects.get(
                    title='Digithup').frontend_temp + '/modal.html',
                'FRONTEND_JS': 'frontend/' + SystemSetting.objects.get(title='Digithup').frontend_temp + '/js.html',

            }






    except Exception as e:

        return {
            'BASE_USE': 'good',
            'TEMPLATES_USE': 'good',
            'FOOTER_USE': 'good',
            'JS_USE': 'good',
        }





def user_processors(request):
    if not request.user.is_authenticated:
        return {
            'user_address': None,
            'user_mode': None,
            'wish_count': None,


        }
    current_user = User.objects.get(id=request.user.id)
    try:
        employee_access = None

        if current_user.access_level == 'Employee':

            access = 'Employee'

        elif current_user.access_level == 'Owner':
            access = 'Owner'
        elif current_user.access_level == 'ThirdPartyService':
            access = 'ThirdPartyService'
        elif current_user.access_level == 'Customer':
            access = 'Customer'
        elif current_user.access_level == 'SuperAdmin':
            access = 'SuperAdmin'
        elif current_user.access_level == 'Admin':
            access = 'Admin'
        elif current_user.access_level == 'Staff':
            access = 'Staff'
        else:
            access = None

        return {
            'current_user':current_user,
            'user_access': access,
            'employee_access': employee_access,

        }
    except BaseException as e:

        return {
            'current_user': current_user,
            'user_access': None,
            'employee_access': None,

        }


def notifications(request):
    one_week_ago = datetime.now() - timedelta(days=1)
    one_week_next = datetime.now() + timedelta(days=7)
    try:
        if not request.user.is_authenticated:
            return {
                'admin_notifications': None,
            }
        user = User.objects.get(id=request.user.id)
        context_notifications = Notification.objects.filter(receiver_model=ContentType.objects.get(model='User'),
                                                            receiver_id=user.id,
                                                            is_read=False, notification_time__gte=one_week_ago,
                                                            notification_time__lt=one_week_next).order_by('-id')[:4]
        notification_count = Notification.objects.filter(receiver_model=ContentType.objects.get(model='User'),
                                                         receiver_id=user.id,
                                                         is_read=False, notification_time__gte=one_week_ago,
                                                         notification_time__lt=one_week_next).count()
        allnotifications = Notification.objects.all()

        return {
            'context_notifications': context_notifications,
            'notification_count': notification_count,
            'notifications': allnotifications
        }



    except Exception as e:

        admin = User.objects.get(is_superuser=True)
        if not request.user.is_authenticated:
            return {
                'admin_notifications': request.user.notifications.filter(is_read=False, to_user=admin,
                                                                         extra_time__gte=one_week_ago,
                                                                         extra_time__lt=one_week_next),
                'seller_notifications': None,
                'deliver_notifications': None,

            }
        admin = User.objects.filter(is_superuser=True)

        if request.user.is_authenticated and admin:
            return {'admin_notifications': None}



