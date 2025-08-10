# In your chat/views.py

import logging
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.db.models import Q
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models.chat import Dialog, Message # Assuming you still have these models
from helper.commonHelper import ACTIVE_FRONTEND_TEMPLATES

User = get_user_model()
logger = logging.getLogger(__name__)

def get_dialog_id(user1_pk, user2_pk):
    """Creates a predictable, unique dialog ID for any two users."""
    # Sort the user IDs to ensure the same ID is generated regardless of who starts the chat
    if user1_pk > user2_pk:
        return f"{user2_pk}_{user1_pk}"
    else:
        return f"{user1_pk}_{user2_pk}"

@login_required
def start_chat_view(request, user_id):
    """
    Generates a predictable dialog ID and redirects to the chat room.
    This view no longer needs to interact with the Dialog model directly.
    """
    other_user = get_object_or_404(User, id=user_id)

    if request.user == other_user:
        raise Http404("You cannot start a chat with yourself.")

    # Generate the predictable dialog ID for Firebase
    dialog_id = get_dialog_id(request.user.pk, other_user.pk)

    # Redirect to the chat room view, which will handle rendering
    return redirect('FrontChatRoom', dialog_id=dialog_id)


@login_required
def chat_room_view(request, dialog_id):
    """
    Renders the main chat page.
    It determines the other user from the dialog_id and passes context to the template.
    It no longer fetches messages, as that is handled by Firebase on the frontend.
    """
    try:
        # Extract user IDs from the dialog_id string
        user_ids = dialog_id.split('_')
        user1_pk = int(user_ids[0])
        user2_pk = int(user_ids[1])

        # Determine which ID belongs to the other user
        if request.user.pk == user1_pk:
            other_user_pk = user2_pk
        elif request.user.pk == user2_pk:
            other_user_pk = user1_pk
        else:
            # If the current user is not part of this chat, deny access.
            logger.warning(f"User {request.user.id} attempted to access unauthorized chat {dialog_id}")
            raise Http404("You do not have permission to view this chat.")

        other_user = get_object_or_404(User, pk=other_user_pk)

        context = {
            'dialog_id': dialog_id,
            'other_user': other_user,
            # Note: We no longer pass 'messages' from Django.
            # The Vue app will fetch them from Firebase.
        }
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/chat.html', context)

    except (ValueError, IndexError, User.DoesNotExist):
        logger.error(f"Invalid dialog_id format or user not found for dialog_id: {dialog_id}", exc_info=True)
        raise Http404("Invalid chat session.")
    except Exception as e:
        logger.error(f"Error in chat_room_view for dialog {dialog_id}: {str(e)}", exc_info=True)
        raise Http404(f"Error loading chat: {str(e)}")


@login_required
def dialog_list_view(request):
    """
    API endpoint to fetch the list of dialogs for the left sidebar.
    This logic can remain, but it now needs to generate the same predictable dialog_id.
    """
    # This query assumes you still create Dialog objects when a message is first saved.
    # If not, you may need a different way to get the list of users someone has chatted with.
    dialogs = Dialog.objects.filter(Q(provider=request.user) | Q(customer=request.user)).select_related('provider', 'customer').prefetch_related('messages')

    data = []
    for dialog in dialogs:
        other_user = dialog.provider if request.user == dialog.customer else dialog.customer
        last_message = dialog.messages.last()
        data.append({
            # Generate the same predictable ID for the href
            'dialog_id': get_dialog_id(request.user.pk, other_user.pk),
            'other_user': {
                'id': other_user.id,
                'name': other_user.get_full_name(),
                'image_url': other_user.image.url if other_user.image and hasattr(other_user.image, 'url') else None,
            },
            'last_message': last_message.content if last_message else 'No messages yet.',
            'last_message_time': last_message.created_at.isoformat() if last_message else '',
        })
    return JsonResponse(data, safe=False)


class SaveChatMessageAPI(APIView):
    """
    API endpoint for the Firebase Function to call.
    It saves a message to the Django database for persistent storage.
    """
    # In a production environment, you should add authentication
    # (e.g., a secret key shared between this API and the Firebase Function).
    def post(self, request, *args, **kwargs):
        dialog_id_str = request.data.get('dialog_id')
        sender_id = request.data.get('sender')
        receiver_id = request.data.get('receiver')
        text = request.data.get('text')

        if not all([dialog_id_str, sender_id, text, receiver_id]):
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = User.objects.get(pk=sender_id)
            receiver = User.objects.get(pk=receiver_id)

            # Find or create the dialog in your database
            # This ensures you have a record of the conversation.
            dialog, created = Dialog.objects.get_or_create_dialog_between(sender, receiver)

            # Create the message in your Django DB
            Message.objects.create(
                dialog=dialog,
                sender=sender,
                content=text
            )
            return Response({"success": "Message saved"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error saving message from Firebase: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

