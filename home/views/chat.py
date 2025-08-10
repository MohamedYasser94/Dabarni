# In views.py
import logging
from django.contrib.auth import get_user_model, aget_user
from django.shortcuts import render, redirect, get_object_or_404, aget_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models.chat import Dialog, Message
from helper.commonHelper import ACTIVE_FRONTEND_TEMPLATES

User = get_user_model()
logger = logging.getLogger(__name__)


# RECOMMENDED: Revert to the simpler and more efficient get_or_create
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
        logger.info(f"Found existing dialog between {user1.get_full_name()} and {user2.get_full_name()}, ID: {dialog.id}")

    return dialog



@login_required
def start_chat_view(request, user_id):
    """
    View to find or create a dialog between the logged-in user and another user.
    """
    try:
        # CHANGED: Use the synchronous version to get a real User object
        other_user = get_object_or_404(User, id=user_id)

        # CHANGED: Get the current user directly from the request (synchronous)
        current_user = request.user

        if current_user.id == other_user.id:
            # You already have a duplicate check, but checking the ID can be safer
            # in case of proxy models.
            raise Http404("You cannot start a chat with yourself.")

        # This call will now work perfectly
        dialog = get_or_create_dialog_between(current_user, other_user)

        redirect_url = reverse('home:FrontChatRoom', kwargs={'dialog_id': dialog.id})
        logger.info(f"Redirecting to chat for user {current_user.id} with user {user_id}, dialog ID: {dialog.id}")
        return HttpResponseRedirect(redirect_url)

    except User.DoesNotExist:
        raise Http404("The user you are trying to chat with does not exist.")
    except Exception as e:
        logger.error(f"Error in start_chat_view for user {user_id}: {str(e)}", exc_info=True)
        raise Http404("An error occurred while trying to start the chat.")

@login_required
def chat_room_view(request, dialog_id):
    """
    This view renders the main chat page (chat.html).
    The template will then use the dialog_id to connect to the WebSocket.
    """
    try:
        dialog = get_object_or_404(Dialog.objects.prefetch_related('messages__sender'), id=dialog_id)
        if request.user not in [dialog.provider, dialog.customer]:
            logger.warning(f"User {request.user.id} not authorized for dialog {dialog_id}")
            raise Http404("You do not have permission to view this chat.")

        # Fetch initial messages and serialize to JSON-compatible format
        messages = dialog.messages.select_related('sender').all().order_by('created_at')[:50]
        messages_serialized = []
        for msg in messages:
            messages_serialized.append({
                'text': msg.content,
                'sender': msg.sender.id,
                'sender_username': msg.sender.get_full_name(),
                'created_at': msg.created_at.isoformat(),
            })

        # Prepare other_user data, ensuring image URL is valid
        other_user = dialog.provider if request.user == dialog.customer else dialog.customer
        other_user_data = {
            'pk': other_user.pk,
            'get_full_name': other_user.get_full_name(),
            'image_url': other_user.image.url if other_user.image and hasattr(other_user.image, 'url') else '/static/digithup/b.png',
        }

        import json
        context = {
            'dialog_id': str(dialog_id),
            'messages': json.dumps(messages_serialized),
            'other_user': other_user_data,
        }
        logger.info(f"Rendering chat room for dialog {dialog_id}, user {request.user.id}")
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/chat.html', context)
    except Exception as e:
        logger.error(f"Error in chat_room_view for dialog {dialog_id}: {str(e)}", exc_info=True)
        raise Http404(f"Error loading chat: {str(e)}")

@login_required
def dialog_list_view(request):
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
                    'id': other_user.id,
                    'name': other_user.get_full_name(),
                    'image_url': other_user.image.url if other_user.image and hasattr(other_user.image, 'url') else None,
                },
                'last_message': last_message.content if last_message else '',
                'last_message_time': last_message.created_at.isoformat() if last_message else '',
            })
        logger.info(f"Fetched dialog list for user {request.user.id}, count: {len(data)}")
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"Error in dialog_list_view for user {request.user.id}: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Failed to load dialogs'}, status=500)


class SaveChatMessageAPI(APIView):
    # Add authentication & permission classes if needed
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        dialog_id = request.data.get('dialog_id')
        sender_id = request.data.get('sender')
        text = request.data.get('text')

        if not all([dialog_id, sender_id, text]):
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Here you would look up your Dialog/Chat model
            # and save the message. This is a simplified example.
            sender = User.objects.get(pk=sender_id)
            # dialog = ChatDialog.objects.get(id=dialog_id)
            Message.objects.create(
                # dialog=dialog,
                sender=sender,
                text=text
            )
            return Response({"success": "Message saved"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
