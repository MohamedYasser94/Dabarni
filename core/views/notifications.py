from datetime import datetime

import firebase_admin
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
# from fcm_django.models import FCMDevice
from firebase_admin import credentials, auth, firestore, messaging
from firebase_admin.messaging import Message, Notification

from core.models.notifications import Notification
from Dabarni import settings
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staff, staff_only

User = get_user_model()





@authenticated_staff
@staff_only
def AdminNotificationslist(request):
    notifications = Notification.objects.filter( receiver_model=ContentType.objects.get(model='User'),
                                                    receiver_id=request.user.id).order_by('-created_at')


    return render(request, f'{BACKEND_TEMPLATES}/notification/notifications.html', {'notifications': notifications})
@authenticated_staff
@staff_only
def AdminNotificationsDetails(request,slug):
    notification = Notification.objects.get(slug=slug)
    notification.is_read = True
    notification.save()
    domain = Site.objects.get_current().domain
    path = notification.owner.get_absolute_url()
    url = '{domain}{path}'.format(domain=domain, path=path)
    print('url', url)
    return HttpResponseRedirect(url)






@login_required
def vendor_notifications(request):
    if request.user.is_authenticated and request.user.seller:
        goto = request.GET.get('goto', '')
        notification_id = request.GET.get('notification', 0)
        extra_id = request.GET.get('extra_id', 0)
        notification_list = Notification.objects.filter(is_read=False)
        page = request.GET.get('page', 1)

        paginator = Paginator(notification_list, 10)
        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            notifications = paginator.page(1)
        except EmptyPage:
            notifications = paginator.page(paginator.num_pages)

        if goto != '':
            notification = Notification.objects.get(pk=notification_id)
            notification.is_read = True
            notification.save()
            if notification.notification_type in [
                Notification.MESSAGE,
                Notification.APPLICATION,
                Notification.NewOrder,
                Notification.NewRegistration,
                Notification.NewVendorCreate,
            ]:
                return redirect('view_application', application_id=notification.extra_id)
        return render(request, 'notification/vendor_notifications.html', {'notifications': notifications})


@login_required
def shipping_notifications(request):
    if request.user.is_authenticated and request.user.deliver:
        goto = request.GET.get('goto', '')
        notification_id = request.GET.get('notification', 0)
        extra_id = request.GET.get('extra_id', 0)
        notification_list = Notification.objects.filter(is_read=False)
        page = request.GET.get('page', 1)

        paginator = Paginator(notification_list, 10)
        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            notifications = paginator.page(1)
        except EmptyPage:
            notifications = paginator.page(paginator.num_pages)

        if goto != '':
            notification = Notification.objects.get(pk=notification_id)
            notification.is_read = True
            notification.save()
            if notification.notification_type in [
                Notification.MESSAGE,
                Notification.APPLICATION,
                Notification.NewOrder,
                Notification.NewRegistration,
                Notification.NewVendorCreate,
            ]:
                return redirect('view_application', application_id=notification.extra_id)
        return render(request, 'notification/shipping_notifications.html', {'notifications': notifications})



def AdminCommonNotifications(request, notification_type, is_read, second_read, is_confirmed, notification,
                             notification_url,notification_slug, notification_info,
                             notification_desc, notification_time, notification_notify, sender_model, sender_id,
                             receiver_model, receiver_id, owner_model, owner_id, auditor_model, auditor_id):
    print('notification_type')
    notification_object= Notification(notification_type=notification_type, is_read=is_read, second_read=second_read,
                                       is_confirmed=is_confirmed, notification=notification,
                                       notification_url=notification_url,notification_slug=notification_slug, notification_info=notification_info,
                                       notification_desc=notification_desc, notification_time=notification_time,
                                       notification_notify=notification_notify, sender_model=ContentType.objects.get(model=sender_model),
                                       sender_id=sender_id, receiver_model=ContentType.objects.get(model=receiver_model), receiver_id=receiver_id,
                                       owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id, auditor_model=ContentType.objects.get(model=auditor_model),
                                       auditor_id=auditor_id)
    notification_object.save()
    # return (notification_object.receiver_id,notification_object.notification_type)


@login_required
def chat_notifications(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')
    goto = request.GET.get('goto', '')
    notification_id = request.GET.get('notification', 0)
    extra_id = request.GET.get('extra_id', 0)
    notification_list = Notification.objects.filter(is_read=False, to_user=request.user)
    page = request.GET.get('page', 1)

    paginator = Paginator(notification_list, 10)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    if goto != '':
        notification = Notification.objects.get(pk=notification_id)
        notification.is_read = True
        notification.save()
        if notification.notification_type in [
            Notification.MESSAGE,
            Notification.APPLICATION,
            Notification.NewRegistration,
            notification.NewCasesCreate,
            notification.CasesUpdate,

            notification.NoteCasesCreate,
            notification.CasesRemember,
            notification.CasesArchive,

        ]:
            return redirect('view_application', application_id=notification.extra_id)
    return render(request, f'{BACKEND_TEMPLATES}/notification/notifications.html', {'notifications': notifications})


def FcmNotifications(request,slug,message_title,message_body):
    try:

        user = User.objects.get(slug=slug)
        print('user', user.id,slug)
        message = messaging.Message(
            notification=messaging.Notification(
                title=message_title,
                body=message_body,

            ),
            token=user.fcm_token,
        )
        # message = messaging.Message(
        #     data={
        #         'score': '850',
        #         'time': '2:45',
        #     },
        #     token=user.fcm_token,
        # )
        # message = messaging.Message(
        #     notification=messaging.Notification(
        #         title='This is a Notification Title',
        #         body='This is a Notification Body',
        #     ),
        #     data={
        #         'order_id': '850',
        #         'time': '2:45',
        #     },
        #     token=user.fcm_token,)

        # device = FCMDevice.objects.get(user_id=user.id)
        # device.send_message( message)
        # device.send_message(Message(notification=Notification(title=message_title, body=message_body)))
        print('message sent')


    except Exception as e:
        print('FcmNotifications error', e)
