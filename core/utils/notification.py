import asyncio

import aiohttp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


from core.models.core import *
from core.models.notifications import*


from core.models.social import *
from core.utils.whatsapp import *
from Dabarni.settings import *
from helper.commonHelper import *

User = get_user_model()


############ Enmail  Notifcation ##################

def notify_admin(request, name, email, phone, subject, message):
    from_email = settings.DEFAULT_EMAIL_FROM
    site_setting = SiteSetting.objects.all()
    for setting in site_setting:
        to_email = setting.email
        subject = subject
        text_content = message
        context = {'title': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message, }
        html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/notification/email_notify_user.html',
                                        context)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()


def notify_user(request, name, email, phone, subject, message, url, button_text, button_url, button_text2, button_url2):
    site_setting = SiteSetting.objects.all()
    system_setting = SystemSetting.objects.get(status='Active')
    if system_setting.email_host != None or system_setting.email_host != '' or settings.email_user != None or settings.email_user != '' or settings.email_pass != None or settings.email_pass != '' or settings.email_port != None or settings.email_port != '' or settings.email_use_tls != None or settings.email_use_tls != '':
        email_host = system_setting.email_host
        email_user = system_setting.email_user
        email_pass = system_setting.email_pass
        email_port = system_setting.email_port
        email_use_tls = system_setting.email_use_tls
        from_email = email_user
    else:

        from_email = settings.EMAIL_HOST_USER

    subject = subject
    text_content = message
    context = {'title': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message, 'url': url,
        'button_text': button_text, 'button_url': button_url, 'button_text2': button_text2, 'button_url2': button_url2,

    }
    html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/notification/email_notify_user.html', context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
async def delay_function():
    await asyncio.sleep(1)

# Call the delay_function() function from a synchronous function
asyncio.run(delay_function())


def notify_user_ticket(request, slug, message):

    client = User.objects.get(slug=slug)


    name = f'Dear, {client.title} {client.first_name} {client.middle_name}'
    email = client.email
    phone = client.phone
    if client.data_confirmed == 'Active':
        subject = _(f'your invitation Created in ')
    else:
        subject = _(f'your invitation request in ')
    message = message
    url = (f'{request._current_scheme_host}')
    button_text = 'View Event'
    button_url = (f'{request._current_scheme_host}')
    button_text2 = 'View Ticket'
    button_url2 = (f'{request._current_scheme_host}')
    # image_url = (f'{request._current_scheme_host}{attendee.card_image.url}')
    ticket_code = ''


    site_setting = SiteSetting.objects.all()
    system_setting = SystemSetting.objects.get(status='Active')
    if system_setting.email_host != None or system_setting.email_host != '' or settings.email_user != None or settings.email_user != '' or settings.email_pass != None or settings.email_pass != '' or settings.email_port != None or settings.email_port != '' or settings.email_use_tls != None or settings.email_use_tls != '':
        email_host = system_setting.email_host
        email_user = system_setting.email_user
        email_pass = system_setting.email_pass
        email_port = system_setting.email_port
        email_use_tls = system_setting.email_use_tls
        from_email = email_user
    else:

        from_email = settings.EMAIL_HOST_USER

    subject = subject
    text_content = message
    context = {'title': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message, 'url': url,
        'button_text': button_text, 'button_url': button_url, 'button_text2': button_text2, 'button_url2': button_url2,
        # 'image_url': image_url,


    }
    if client.data_confirmed == 'Active':
        html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/ticket/ticket.html', context)
    else:
        html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/ticket/request.html', context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, 'text/html')

    msg.send()


def CommonWhatappNotification(request, name, phone, message):
    messenger = WhatsApp(WhatsApp_TOKEN, phone_number_id=WhatsApp_phone_number)
    # messenger.send_message(title, phone)
    messenger.send_message(message, phone)
    messenger.send_location(lat=1.29, long=103.85, name="Singapore", address="Singapore",
        recipient_id="+201015666808", )

    response = messenger.send_message(

        message=message, recipient_id=phone, )
    print('whatapp response', response)


async def send_whatsapp_message(phone_number, message):
    """Sends a WhatsApp message using asyncio."""
    url = f'https://api.whatsapp.com/send?phone={phone_number}&text={message}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                print('Message sent successfully.')
            else:
                print('Failed to send message.')





############ Dashboard Notifcation ##################

def create_notification_admin(request, to_user, notification_type, extra_id=None, extra_slug=None, extra_info=None,
                              more_info=None, extra_time=None, extra_notify=None):
    notification = Notification.objects.create(to_user=to_user, notification_type=notification_type, is_read=False,
                                               second_read=False, is_confirmed=False, extra_id=extra_id,
                                               extra_slug=extra_slug, extra_info=extra_info, more_info=more_info,
                                               extra_time=extra_time, extra_notify=extra_notify)


def create_notification_vendor(request, to_user, notification_type, court_info=0, extra_id=0, extra_info=0,
                               extra_time=None, extra_notify=None, extra_slug=0):
    notification = Notification.objects.create(to_user=to_user, notification_type=notification_type,
                                               court_info=court_info, extra_time=extra_time, extra_notify=extra_notify,
                                               extra_slug=extra_slug, extra_id=extra_id, extra_info=extra_info)


def notify_vendor(detail, subject, text_content):
    from_email = settings.DEFAULT_EMAIL_FROM
    vendor = User.objects.get(id=detail.vendor.id)
    print('vensor data', detail)

    to_email = vendor.email
    subject = subject
    text_content = text_content
    html_content = render_to_string(f'{BACKEND_TEMPLATES}/notification/email/vendor.html',
                                    {'data': detail, 'vendor': vendor})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()





def create_notification_chat(request, target, from_user, object_id):
    print('content_type', object_id)
    content = ContentType.objects.get_for_model(FriendList)
    redirect_url = f"{settings.BASE_URL}/profile/{from_user.slug}/",
    verb = f"Sent To Yoy Follow {from_user.email}.",

    notification = ChatNotification.objects.create(target=target, from_user=from_user, content_type=content,
                                                   object_id=object_id, redirect_url=redirect_url, verb=verb,
                                                   read=False)
