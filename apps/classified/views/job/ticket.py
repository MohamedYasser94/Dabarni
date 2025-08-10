from decimal import Decimal

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from apps.classified.forms.job import *
from apps.classified.forms.ticket import AdminReportMessageForm, AdminTicketMessageForm
from apps.classified.models.job import *
from apps.classified.models.ticket import Report, SupportTicket, TicketMessage, ReportMessage
from core.utils.backends import RandomPasswordGenerator
from helper.commonHelper import *
from helper.decorators import *
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials, firestore

from apps.classified.models.ticket import SupportTicket, TicketMessage
from helper.decorators import authenticated_staff, staff_only
User = get_user_model()


##################### Job Ticket #####################
@authenticated_staff
@staff_only
def AdminJobTicketList(request):
    tickets = SupportTicket.objects.all().order_by('-id')
    context = {
        'tickets': tickets,
        'title': _('Job Ticket List'),
        'page_title': _('Job Ticket List'),
        'page_icon': 'fa fa-ticket',
        'back_url': reverse_lazy('classified:AdminJobTicketList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/ticket/admin.html', context)


@authenticated_staff
@staff_only
def AdminJobTicketDetails(request, slug):
    """
    This view now correctly renders the real-time chat template.
    It passes the necessary data for the Vue.js application to connect to Firebase.
    """
    ticket = get_object_or_404(SupportTicket, slug=slug)

    # This view's only job is to render the page with the chat app.
    # The Vue app will fetch and display messages from Firebase.
    context = {
        'ticket': ticket,
        'title': _('Reply to Ticket'),
        'page_title': _('Reply to Ticket'),
        'page_icon': 'fa fa-comments',
        'back_url': reverse_lazy('classified:AdminJobTicketList'),
    }
    # IMPORTANT: Ensure you are rendering the template that contains the Vue.js chat code.
    # Based on previous files, this should be 'ticket_replay.html'.
    return render(request, f'{BACKEND_TEMPLATES}/job/ticket/ticket_replay.html', context)


# FIX 1: Create a new API view to save admin messages sent from the Vue app
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensures only logged-in users (admins) can use it
def ApiAdminSaveTicketMessage(request, ticket_id):
    """
    Saves a message sent from the admin chat interface to the Django database.
    """
    try:
        ticket = SupportTicket.objects.get(id=ticket_id)
        message_text = request.data.get('text')

        if not message_text:
            return Response({"error": "Message text is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the message to the Django database
        TicketMessage.objects.create(
            ticket=ticket,
            user=request.user,
            message=message_text,
            user_type='admin'  # Mark this message as from an admin
        )
        return Response({"success": "Message saved to DB"}, status=status.HTTP_201_CREATED)
    except SupportTicket.DoesNotExist:
        return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



##########################      Blog Category Admin            ################################

@authenticated_staff
@staff_only
def AdminJobReportList(request):
    reports = Report.objects.all().order_by(
        '-created_at')


    context = {
        'reports': reports,
        'title': _('Job Report List'),
        'page_title': _('Job Report List'),
        'page_icon': 'fa fa-list',
        'back_url': reverse_lazy('classified:AdminJobReportList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/job/report/admin.html', context)


@authenticated_staff
@staff_only
def AdminJobReportDetails(request, report_slug):
    """
    This view now renders the Firebase chat interface for a single report.
    """
    try:
        report = get_object_or_404(Report, slug=report_slug)

        # Prepare the context needed for the Vue.js chat app
        context = {
            'report': report,  # Pass the whole report object
            'title': _('Report Details'),
            'page_title': _('Report Details'),
            'page_icon': 'fa fa-comments',
            'back_url': reverse_lazy('job:AdminJobReportList'),  # Use your app's namespace
        }
        # Render the new chat template for reports
        return render(request, f'{BACKEND_TEMPLATES}/job/report/report_replay.html', context)

    except Report.DoesNotExist:
        messages.error(request, _('Report not found.'))
        return HttpResponseRedirect(reverse_lazy('job:AdminJobReportList'))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiAdminSaveReportMessage(request, report_id):
    """
    Saves a message sent from the admin report chat interface to the Django database.
    """
    try:
        report = Report.objects.get(id=report_id)
        message_text = request.data.get('text')

        if not message_text:
            return Response({"error": "Message text is required."}, status=status.HTTP_400_BAD_REQUEST)

        ReportMessage.objects.create(
            report=report,
            user=request.user,
            message=message_text,
            user_type='admin'
        )
        return Response({"success": "Message saved to DB"}, status=status.HTTP_201_CREATED)
    except Report.DoesNotExist:
        return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@authenticated_staff
@staff_only
def AdminJobReportMessageCreate(request, report_id):
    report = Report.objects.filter(id=report_id).first()
    if not report:
        messages.error(request, _('Report not found.'))
        return HttpResponseRedirect(reverse_lazy('classified:AdminJobReportList'))

    if request.method == 'POST':
        form = AdminReportMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.report = report
            message.user = request.user
            message.save()
            messages.success(request, _('Message added successfully.'))
            return HttpResponseRedirect(reverse_lazy('classified:AdminJobReportMessageList') + f'?report_id={report.id}')
    else:
        form = AdminReportMessageForm()

    context = {
        'form': form,
        'report': report,
        'title': _('Add Report Message'),
        'page_title': _('Add Report Message'),
        'page_icon': 'fa fa-plus',
        'back_url': reverse_lazy('classified:AdminJobReportMessageList') + f'?report_id={report.id}',
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/report/message/create.html', context)




