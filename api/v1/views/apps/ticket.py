# In api/v1/views/ticket.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from api.v1.serializers.app.ticket import *
from apps.classified.models.job import JobRequest
import firebase_admin
from firebase_admin import credentials, firestore


# --- Helper function to send data to Firebase ---
def send_message_to_firestore(collection_name, doc_slug, message_data):
    try:
        db = firestore.client()
        # Ensure createdAt is a server timestamp for correct ordering
        message_data['createdAt'] = firestore.SERVER_TIMESTAMP
        db.collection(collection_name).document(str(doc_slug)).collection("messages").add(message_data)
        print(f"SUCCESS: Message for ticket {doc_slug} sent to Firestore collection '{collection_name}'.")
    except Exception as e:
        print(f"ERROR: Failed to send message to Firestore. Reason: {e}")




###################### Ticket API Views ######################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiSupportTicketCreate(request):
    """
    Creates a new support ticket using the serializer for validation.
    """
    serializer = SupportTicketSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        response_data = {
            "message": "Ticket created successfully",
            "ticket_info": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])  # Changed to GET as it's a retrieval operation
@permission_classes([IsAuthenticated])
def ApiSupportTicketList(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-create_at')
    serializer = SupportTicketSerializer(tickets, many=True)
    response_data = {
        "buyer_slug": request.user.id,
        "tickets": {
            "data": serializer.data,
            "current_page": 1,
            "last_page": 1,
            "total": tickets.count()
        }
    }
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiSupportTicketDetail(request, id):
    try:
        ticket = SupportTicket.objects.get(id=id, user=request.user)
        messages_qs = ticket.messages.all().order_by('create_at')
        serializer = TicketMessageSerializer(messages_qs, many=True)
        return Response({
            "ticket_slug": str(ticket.id),
            "all_messages": serializer.data
        })
    except SupportTicket.DoesNotExist:
        return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def ApiSupportTicketMessageSend(request):
    ticket_slug = request.data.get('ticket_slug')
    message_text = request.data.get('message')
    attachment_file = request.data.get('attachment')

    if not ticket_slug:
        return Response({"error": "Ticket ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    if not message_text and not attachment_file:
        return Response({"error": "Message or attachment is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Ensure the ticket exists and belongs to the user
        ticket = SupportTicket.objects.get(slug=ticket_slug, user=request.user)

        # 1. Save the message to your local Django database
        TicketMessage.objects.create(
            ticket=ticket,
            user=request.user,
            message=message_text or "", # ensure message is not null
            attachment=attachment_file,
            user_type='buyer'
        )
        print(f"SUCCESS: Message for ticket {ticket.slug} saved to Django DB.")

        # 2. Prepare the message data for Firebase
        firestore_message = {
            'text': message_text or "",
            'sender_is': request.user.slug,
            'sender_type': 'buyer',
            'receiver_is': None, # Admin is the implied receiver
            # 'attachment_url': '...' # TODO: Handle file uploads to cloud storage
        }

        # 3. Send the prepared message to Firebase
        send_message_to_firestore('ticket_chats', ticket.slug, firestore_message)

        return Response({"message": "Message sent successfully"}, status=status.HTTP_201_CREATED)
    except SupportTicket.DoesNotExist:
        return Response({"error": "Ticket not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in ApiSupportTicketMessageSend: {e}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################ Report Api ############################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiCreateReport(request):
    """
    Creates a new report for a specific order.
    """
    order_slug = request.data.get('order_slug')
    service_slug = request.data.get('service_slug')
    report_message = request.data.get('report')

    print('DEBUG: Creating report with data:', request.data)

    if not all([order_slug, service_slug, report_message]):
        return Response({"message": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a report for this order already exists
    if Report.objects.filter(order_slug=order_slug, buyer=request.user).exists():
        return Response({"message": "A report for this order has already been submitted."},
                        status=status.HTTP_409_CONFLICT)

    try:
        # Find the service and seller from the service slug
        job_request = JobRequest.objects.filter(slug=service_slug).first()
        if job_request:
            service = job_request.classified_job
            seller = job_request.classified_job.provider.user
        else:
            # If not found in JobRequest, try to find it in Job
            service = Job.objects.get(slug=service_slug)
            seller = service.provider.user


    except Job.DoesNotExist:
        return Response({"message": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

    # The Report model's save() method will automatically generate the slug
    Report.objects.create(
        buyer=request.user,
        seller=seller,
        service=service,
        order_slug=order_slug,
        report=report_message
    )

    return Response({"message": "Report submitted successfully"}, status=status.HTTP_201_CREATED)


# FIX: This view is updated for consistency and uses GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiReportList(request):
    """
    Lists all reports filed by the currently authenticated user.
    """
    reports = Report.objects.filter(buyer=request.user).order_by('-created_at')
    serializer = ReportSerializer(reports, many=True)
    return Response({"data": serializer.data})


# NEW: Add a view to check if a report exists for an order
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiCheckReportExists(request, order_id):
    """
    Checks if a report has been filed for a specific order by the current user.
    """
    exists = Report.objects.filter(order_id=order_id, buyer=request.user).exists()
    return Response({'exists': exists})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiReportDetail(request, slug):
    try:
        report = Report.objects.get(slug=slug, buyer=request.user)
        messages = report.messages.all().order_by('created_at')
        serializer = ReportMessageSerializer(messages, many=True)
        # FIX: The JSON response now matches the ReportMessageModel in Flutter.
        response_data = {
            "ticket_slug": str(report.slug),  # Changed 'report_slug' to 'ticket_slug'
            "all_messages": serializer.data,
            "q": ""
        }
        return Response(response_data)
    except Report.DoesNotExist:
        return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def ApiReportMessageSend(request):
    report_slug = request.data.get('report_slug')
    message_text = request.data.get('message')
    attachment_file = request.data.get('attachment')

    if not report_slug:
        return Response({"error": "Report slug is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Find the report by slug and ensure it belongs to the user
        report = Report.objects.get(slug=report_slug, buyer=request.user)

        # 1. Save to Django DB
        ReportMessage.objects.create(
            report=report, user=request.user, message=message_text or "",
            attachment=attachment_file, user_type='buyer'
        )

        # 2. Prepare and send to Firebase using the slug
        firestore_message = {
            'text': message_text or "",
            'sender_slug': request.user.slug,
            'sender_type': 'buyer',
        }
        send_message_to_firestore('report_chats', report.slug, firestore_message)

        return Response({"message": "Message sent successfully"}, status=status.HTTP_201_CREATED)
    except Report.DoesNotExist:
        return Response({"error": "Report not found or you do not have permission."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiAddServiceRating(request, service_slug):
    """
    Creates a new rating for a specific service (Job), identified by its slug.
    """
    job = None
    # Try to find the Job directly by its slug
    job_qs = Job.objects.filter(slug=service_slug)
    if job_qs.exists():
        job = job_qs.first()
    else:
        # If not found, check if the slug belongs to a JobRequest
        job_request_qs = JobRequest.objects.filter(slug=service_slug)
        if job_request_qs.exists():
            job = job_request_qs.first().classified_job

    if job is None:
        return Response({"error": "Service not found for the given slug."}, status=status.HTTP_404_NOT_FOUND)

    # Now, validate the incoming review data
    serializer = ServiceReviewSerializer(data=request.data)
    if serializer.is_valid():
        # FIX: Pass the job and user objects to the save() method.
        # This provides the missing information to the model.
        serializer.save(job=job, user=request.user)

        # After saving the review, it's good practice to update the job's average rating
        job.update_rating()

        return Response({"message": "Review submitted successfully"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
