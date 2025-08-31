import json
import logging

from urllib.parse import urlencode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from firebase_admin import firestore, messaging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.classified.models.models import JobProgress
from core.models.chat import Dialog
from core.models.chat import Message
from helper.commonHelper import ACTIVE_FRONTEND_TEMPLATES

db = firestore.client()
User = get_user_model()
logger = logging.getLogger(__name__)



def get_or_create_dialog_between(user1, user2):
    """
    Get an existing dialog between two users or create a new one if it doesn't exist.
    This version correctly handles the OR condition.
    """
    # Use .filter() with the Q object to find if a dialog exists in either direction
    dialogs = Dialog.objects.filter(
        Q(provider=user1, customer=user2) | Q(provider=user2, customer=user1)
    )

    if dialogs.exists():
        # If a dialog already exists, get the first one from the QuerySet
        created = False
        dialog = dialogs.first()
    else:
        # If no dialog exists, create a new one
        created = True
        dialog = Dialog.objects.create(provider=user1, customer=user2)

    if created:
        logger.info(f"Created new dialog between {user1.get_full_name()} and {user2.get_full_name()}, ID: {dialog.id}")
    else:
        logger.info(
            f"Found existing dialog between {user1.get_full_name()} and {user2.get_full_name()}, ID: {dialog.id}")

    return dialog


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def StartChatView(request, order_slug):
    """
    Finds or creates a unique chat dialog for a specific order.
    """
    try:
        # 1. Find the order (JobRequest)
        order = get_object_or_404(JobProgress, slug=order_slug)

        # 2. Identify participants
        customer = order.customer
        provider = order.provider.user

        # 3. Ensure the current user is part of this order
        if request.user not in [customer, provider]:
            return JsonResponse({'error': "You are not authorized for this chat."}, status=403)

        # 4. Get or Create a dialog specifically for this job
        dialog, created = Dialog.objects.get_or_create(
            job=order,
            defaults={'provider': provider, 'customer': customer}
        )

        if created:
            logger.info(f"Created new chat dialog for order {order_slug}. Dialog ID: {dialog.id}")
            # Also create the Firestore document on creation
            db.collection('chats').document(str(dialog.id)).set({
                'participant_uids': [provider.firebase_uid, customer.firebase_uid],
                'created_at': firestore.SERVER_TIMESTAMP
            }, merge=True)

        return JsonResponse({
            'dialog_id': str(dialog.id),
            'status': 'success',
            'message': 'Chat dialog ready.'
        }, status=200)

    except JobProgress.DoesNotExist:
        return JsonResponse({'error': "Order not found."}, status=404)
    except Exception as e:
        logger.error(f"Error in start_chat_view for order {order_slug}: {str(e)}", exc_info=True)
        return JsonResponse({'error': "An unexpected server error occurred."}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiProviderChatMessages(request):
    """
    API endpoint to fetch all messages in a dialog based on to_user or dialog_id and page.
    Expects to_user or dialog_id and optional page as query parameters.
    Returns paginated messages compatible with Flutter's ChatMessagesModel.

    """

    print('ApiUserChatAllMessages called', request.body)
    print('ApiUserChatAllMessages called query params', request.GET)
    to_user_slug = request.GET.get('to_user')
    dialog_id = request.GET.get('dialog_id')  # Allow dialog_id as an alternative
    page = request.GET.get('page', '1')  # Default to page 1 if not provided
    per_page = 20  # Adjust pagination size as needed

    if not to_user_slug and not dialog_id:
        return Response({'error': 'to_user or dialog_id is required'}, status=400)

    try:
        current_user = request.user

        # Determine the dialog based on dialog_id or to_user
        dialog = None
        if dialog_id:
            dialog = get_object_or_404(Dialog, id=dialog_id)
        elif to_user_slug:
            to_user = get_object_or_404(User, slug=to_user_slug)
            dialog = Dialog.objects.filter(
                (Q(provider=current_user) & Q(customer=to_user)) |
                (Q(provider=to_user) & Q(customer=current_user))
            ).first()

        if not dialog:
            logger.warning(
                f"No dialog found for dialog_id={dialog_id} or to_user={to_user_slug} by user {current_user.id}")
            return Response({'error': 'No dialog exists with this user.', 'status': 'failed'}, status=404)

        if current_user not in [dialog.provider, dialog.customer]:
            logger.warning(f"User {current_user.id} not authorized for dialog {dialog.id}")
            return Response({'error': 'You do not have permission to view this chat.'}, status=403)

        # Paginate messages
        messages = Message.objects.filter(dialog=dialog).select_related('sender').order_by('created_at')
        total_messages = messages.count()
        start_index = (int(page) - 1) * per_page
        end_index = start_index + per_page
        paginated_messages = messages[start_index:end_index]

        messages_serialized = []
        for msg in paginated_messages:
            other_user = dialog.provider if msg.sender == dialog.customer else dialog.customer
            messages_serialized.append({
                'id': msg.id,
                'from_user': msg.sender.slug,
                'to_user': other_user.slug,
                'message': msg.content,
                'message_type': msg.message_type,  # **NEW**
                'attachment': msg.file_url,  # **NEW**: Use file_url
                'image_url': msg.file.url if msg.file and hasattr(msg.file, 'url') else None,
                'created_at': msg.created_at.isoformat(),
                'updated_at': msg.updated_at.isoformat() if msg.updated_at else None,
                'date_time_str': msg.created_at.isoformat(),
                'date_human_readable': msg.created_at.strftime('%Y-%m-%d %H:%M'),  # Adjust format as needed
                'sender_profile_image': (
                    msg.sender.image.url if msg.sender.image and hasattr(msg.sender.image, 'url') else None),
            })

        response_data = {
            'messages': {
                'current_page': int(page),
                'data': messages_serialized,
                'last_page': (total_messages + per_page - 1) // per_page,  # Ceiling division
                'total': total_messages,
            }
        }

        logger.info(
            f"Fetched messages for dialog {dialog.id} (to_user={to_user_slug}, dialog_id={dialog_id}) by user {current_user.slug}, page {page}")
        return Response(response_data, status=200)

    except User.DoesNotExist:
        logger.warning(f"User with id {to_user_slug} not found when fetching messages for {current_user.slug}.")
        return Response({'error': "The user you are trying to chat with does not exist.", 'status': 'failed'},
                        status=404)
    except ValueError as e:
        logger.error(f"Invalid page or ID format for to_user={to_user_slug} or dialog_id={dialog_id}: {str(e)}")
        return Response({'error': 'Invalid request parameters.', 'status': 'failed'}, status=400)
    except Exception as e:
        logger.error(f"Error fetching messages for to_user={to_user_slug} or dialog_id={dialog_id}: {str(e)}",
                     exc_info=True)
        return Response({'error': 'Failed to load messages', 'status': 'failed'}, status=500)


@login_required
def ChatRoomView(request, dialog_slug):
    """
    This view renders the main chat page (chat.html).
    The template will then use the dialog_id to connect to the WebSocket.
    """
    try:
        dialog = get_object_or_404(Dialog.objects.prefetch_related('messages__sender'), slug=dialog_slug)
        if request.user not in [dialog.provider, dialog.customer]:
            logger.warning(f"User {request.user.id} not authorized for dialog {dialog_slug}")
            raise Http404("You do not have permission to view this chat.")

        # Fetch initial messages and serialize to JSON-compatible format
        messages = dialog.messages.select_related('sender').all().order_by('created_at')[:50]
        messages_serialized = []
        for msg in messages:
            messages_serialized.append({
                'text': msg.content,
                'sender': msg.sender.slug,
                'sender_username': msg.sender.get_full_name(),
                'created_at': msg.created_at.isoformat(),
            })

        # Prepare other_user data, ensuring image URL is valid
        other_user = dialog.provider if request.user == dialog.customer else dialog.customer
        other_user_data = {
            'pk': other_user.pk,
            'get_full_name': other_user.get_full_name(),
            'image_url': other_user.image.url if other_user.image and hasattr(other_user.image,
                                                                              'url') else '/static/digithup/b.png',
        }

        import json
        context = {
            'dialog_id': str(dialog_slug),
            'messages': json.dumps(messages_serialized),
            'other_user': other_user_data,
        }
        logger.info(f"Rendering chat room for dialog {dialog_slug}, user {request.user.slug}")
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/chat.html', context)
    except Exception as e:
        logger.error(f"Error in chat_room_view for dialog {dialog_slug}: {str(e)}", exc_info=True)
        raise Http404(f"Error loading chat: {str(e)}")


@login_required
def DialogListView(request):
    """
    API endpoint to fetch the list of dialogs for the left sidebar.
    """
    try:
        dialogs = Dialog.objects.filter(Q(provider=request.user) | Q(customer=request.user))
        data = []
        for dialog in dialogs:
            other_user = dialog.provider if request.user == dialog.customer else dialog.customer
            last_message = dialog.messages.last()
            data.append({
                'dialog_id': str(dialog.id),
                'other_user': {
                    'slug': other_user.slug,
                    'name': other_user.get_full_name(),
                    'image_url': other_user.image.url if other_user.image and hasattr(other_user.image,
                                                                                      'url') else None,
                },
                'last_message': last_message.content if last_message else '',
                'last_message_time': last_message.created_at.isoformat() if last_message else '',
            })
        logger.info(f"Fetched dialog list for user {request.user.id}, count: {len(data)}")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Error in dialog_list_view for user {request.user.id}: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Failed to load dialogs'}, status=500)


def send_fcm_notification(user, title, body, data=None):
    if user.fcm_token:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=user.fcm_token,
                data=data or {}  # Optional data payload
            )
            messaging.send(message)
            logger.info(f"Sent FCM notification to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send FCM notification to {user.email}: {e}")


# FIX: Converted to a function-based view with decorators and print statements for debugging
@api_view(['POST'])
# permission_classes = [IsAuthenticated] # You can uncomment this later if needed
def SaveChatMessageAPI(request):
    """
    Saves a message sent from the Flutter app to the Django database.
    This is used as a backup for the real-time Firebase messages.
    """
    # Print the entire data payload received from Flutter to debug
    print("--- Save Chat Message API ---")
    print("Received data:", request.data)
    print("Received files:", request.FILES)
    print("---------------------------")

    dialog_slug = request.data.get('dialog_slug')
    sender_slug = request.data.get('sender_slug')  # Assuming Flutter sends the sender's slug
    text = request.data.get('text')
    message_type = request.data.get('message_type', 'text')
    file_url = request.data.get('file_url')  # **NEW**: URL from Firebase
    file = request.FILES.get('file')  # The actual file for backup
    # file = request.FILES.get('file') # To handle file uploads later if needed

    # The 400 error is likely happening here because one of these is missing
    if not all([dialog_slug, sender_slug, text]):
        print("Error: Missing data in request.")
        return Response({"error": "Missing data (dialog_slug, sender_slug, text are required)"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        sender = User.objects.get(slug=sender_slug)
        dialog = Dialog.objects.get(id=dialog_slug)

        # Check if the sender is part of the dialog
        if sender not in [dialog.provider, dialog.customer]:
            print(f"Error: User {sender.slug} is not part of dialog {dialog.id}")
            return Response({"error": "User not authorized for this chat."}, status=status.HTTP_403_FORBIDDEN)

        new_message = Message.objects.create(
            dialog=dialog,
            sender=sender,
            content=text,
            message_type=message_type,
            file_url=file_url,
            file=file
            # file=file # To handle file uploads later
        )
        # --- NOTIFICATION LOGIC ---
        recipient = dialog.provider if sender == dialog.customer else dialog.customer
        notification_title = f"New message from {sender.get_full_name()}"
        notification_body = new_message.content if new_message.content else "Sent an attachment"

        # This will send the push notification
        send_fcm_notification(recipient, notification_title, notification_body)

        print("Success: Message saved to database.")
        return Response({"success": "Message saved"}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        print(f"Error: User with slug '{sender_slug}' not found.")
        return Response({"error": "Sender not found"}, status=status.HTTP_404_NOT_FOUND)
    except Dialog.DoesNotExist:
        print(f"Error: Dialog with id '{dialog_slug}' not found.")
        return Response({"error": "Dialog not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# In api/v1/views/chat.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiUserChatSellerLists(request):
    current_user = request.user

    dialogs = Dialog.objects.filter(
        Q(provider=current_user) | Q(customer=current_user)
    ).select_related('provider', 'customer').prefetch_related('messages__sender')

    chat_seller_lists_data = []

    for dialog in dialogs:
        other_user = dialog.provider if dialog.customer == current_user else dialog.customer

        if other_user is None:
            continue

        last_message = dialog.messages.order_by('-created_at').first()

        last_message_time_str = dialog.created_at.isoformat()
        last_message_content = "No messages yet."

        if last_message:
            last_message_time_str = last_message.created_at.isoformat()
            last_message_content = last_message.content if last_message.content else "Attachment"

        other_user_image_url = None
        if other_user.image and hasattr(other_user.image, 'url'):
            other_user_image_url = request.build_absolute_uri(other_user.image.url)

        seller_list_json = {
            "id": other_user.id,
            "slug": other_user.slug,
            "name": other_user.get_full_name(),
            "email": other_user.email,
            "image": other_user_image_url,
        }

        chat_item = {
            # FIX: Ensure 'dialog_id' is the primary identifier for the dialog.
            # The incorrect 'slug' field has been removed.
            "dialog_id": str(dialog.id),
            "seller_id": other_user.id,
            "seller_slug": other_user.slug,
            "date_time_str": last_message_time_str,
            "last_message_content": last_message_content,
            "seller_list": seller_list_json,
            "imageUrl": other_user_image_url,
        }
        chat_seller_lists_data.append(chat_item)

    return Response({"chat_seller_lists": chat_seller_lists_data})


def ApiUserChatPusherCredentials(request):
    """
    This view provides the Pusher credentials for the user to use in the chat application.
    """
    user = request.user
    if user.is_authenticated:
        pusher_credentials = {
            'app_id': settings.PUSHER_APP_ID,
            'key': settings.PUSHER_KEY,
            'secret': settings.PUSHER_SECRET,
            'cluster': settings.PUSHER_CLUSTER,
            'user_id': user.id,
            'user_info': {
                'name': user.get_full_name(),
                'slug': user.slug
            }
        }
        return JsonResponse(pusher_credentials, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)



