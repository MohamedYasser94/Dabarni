import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter
from firebase_admin import firestore, messaging, auth as firebase_auth
from apps.classified.models.models import JobProgress
from django.core.paginator import Paginator, EmptyPage
from rest_framework.parsers import MultiPartParser, FormParser
try:
    SERVER_TIMESTAMP = firestore.SERVER_TIMESTAMP
except Exception:
    SERVER_TIMESTAMP = None
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models.chat import Dialog, Message, UploadedFile
from django.db.models import Q , Count
from django.utils import timezone
from django.http import JsonResponse
from api.v1.global_serializer.fcm import send_chat_notification

db = firestore.client()
User = get_user_model()
logger = logging.getLogger(__name__)

#----------------------------- Not use for now ----------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_firestore_chats(request):
    """
    Admin function to clean up Firestore chat documents that don't have corresponding database dialogs.
    """
    if not request.user.is_staff:
        return Response({'error': 'Permission denied'}, status=403)

    try:
        chats_ref = db.collection('chats')
        docs = chats_ref.stream()

        cleaned_count = 0
        for doc in docs:
            dialog_id = doc.id

            if not Dialog.objects.filter(id=dialog_id).exists():
                doc.reference.delete()
                cleaned_count += 1
                logger.info(f"Deleted orphaned Firestore chat document: {dialog_id}")

        return Response({
            'message': f'Cleanup completed. Removed {cleaned_count} orphaned chat documents.',
            'cleaned_count': cleaned_count
        }, status=200)

    except Exception as e:
        logger.error(f"Error during Firestore cleanup: {str(e)}")
        return Response({'error': f'Cleanup failed: {str(e)}'}, status=500)


#----------------------------- Helper Functions ----------------------------
def update_firebase_chat_context(dialog, job_progress, provider_user, customer_user):
    try:
        from firebase_admin import firestore
        db = firestore.client()
        dialog_id_str = str(dialog.id)

        data = {
            'participant_uids': [provider_user.firebase_uid, customer_user.firebase_uid],
            'provider_uid': provider_user.firebase_uid,
            'customer_uid': customer_user.firebase_uid,
            'dialog_id': dialog_id_str,
            'dialog_slug': dialog.slug,
            'current_job_slug': job_progress.slug, 
            'updated_at': firestore.SERVER_TIMESTAMP,
        }
        
        db.collection('chats').document(dialog_id_str).set(data, merge=True)
        
    except Exception as e:
        logger.error(f"Firestore Sync Error for dialog {dialog.id}: {str(e)}")
        pass
#----------------------------- API Views -----------------------------------
@extend_schema(tags=["provider chat"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def provider_start_chat_view(request, job_slug):
    """
    Finds existing chat or creates a new one between Customer and Provider.
    Refreshes the Firebase context with the current Job details.
    """
    try:
        current_job_progress = get_object_or_404(JobProgress, slug=job_slug)
        if not current_job_progress.provider:
            return Response(
                {'error': "Job has no provider assigned yet."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        customer = current_job_progress.customer
        provider_profile = current_job_progress.provider 
        provider_user = provider_profile.user
        
        if request.user != customer and request.user != provider_user:
            return Response(
                {'error': "You are not authorized to view this chat."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        if not customer.firebase_uid or not provider_user.firebase_uid:
            logger.error(f"Missing Firebase UID. Customer: {customer.firebase_uid}, Provider: {provider_user.firebase_uid}")
            return Response(
                {'error': "Chat service not available (User UID missing)."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        dialog, created = Dialog.objects.get_or_create(
            provider=provider_user,
            customer=customer,
            defaults={
                'job': current_job_progress.job 
            }
        )
        
        update_firebase_chat_context(dialog, current_job_progress, provider_user, customer)

        provider_slug = getattr(provider_user, 'slug', None)
        customer_slug = getattr(customer, 'slug', None)

        return Response({
            'dialog_id': str(dialog.id),
            'dialog_slug': dialog.slug,
            'status': 'success',
            'is_new': created,
            'participant_uids': {
                'provider': provider_user.firebase_uid,
                'customer': customer.firebase_uid
            },
            'participant_slugs': {
                'provider': provider_slug,
                'customer': customer_slug
            },
            'job_context': {
                'slug': current_job_progress.slug,
                'status': current_job_progress.status
            }
        }, status=status.HTTP_200_OK)

    except JobProgress.DoesNotExist:
        return Response({'error': "Job Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"CRASH: {str(e)} \n {error_details}")
        return Response({
            'error': "Server Error (Debug Mode)",
            'details': str(e),
            'trace': error_details 
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=["provider chat"])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Api_provider_Chat_Lists(request):
    """
    Retrieves a list of chat dialogs for the current user.
    Shows the other participant's details and the last message.
    """
    current_user = request.user
    dialogs = Dialog.objects.filter(
            Q(provider=current_user) | Q(customer=current_user)
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__read=False) & ~Q(messages__sender=current_user)
            )
        ).select_related('provider', 'customer', 'job').prefetch_related('messages')
    chat_seller_lists_data = []

    for dialog in dialogs:
        other_user = dialog.provider if dialog.customer == current_user else dialog.customer
        if other_user is None:
            continue

        last_message = dialog.messages.order_by('-created_at').first()
        if last_message:
            last_activity_time = last_message.created_at
            last_message_content = last_message.content if last_message.content else "Attachment"
        else:
            last_activity_time = dialog.created_at
            last_message_content = ""

        other_user_image_url = None
        try:
            if other_user.image and hasattr(other_user.image, 'url'):
                other_user_image_url = request.build_absolute_uri(other_user.image.url)
        except Exception:
            other_user_image_url = None

        seller_list_json = {
            "id": other_user.id,
            "slug": other_user.slug,
            "name": other_user.get_full_name() if other_user.get_full_name() else other_user.email,
            "email": other_user.email,
            "image": other_user_image_url,
            "is_online": other_user.user_online() if hasattr(other_user, 'user_online') else False
        }

        chat_item = {
            "dialog_id": str(dialog.id),
            "dialog_slug": dialog.slug,
            "dialog_code": dialog.code,
            "customer_id": dialog.customer.id,
            "customer_slug": dialog.customer.slug,
            "provider_id": dialog.provider.id,
            "provider_slug": dialog.provider.slug,
            "job_id": dialog.job.id if dialog.job else None,
            "job_slug": dialog.job.slug if dialog.job else None,
            "job_title": dialog.job.title if dialog.job and hasattr(dialog.job, 'title') else "General Inquiry",
            "date_time_str": last_activity_time.isoformat(),
            "last_message_content": last_message_content,
            "seller_list": seller_list_json,
            "imageUrl": other_user_image_url, 
            "unread_count": dialog.unread_count,
        }
        chat_seller_lists_data.append(chat_item)

    chat_seller_lists_data.sort(key=lambda x: x['date_time_str'] or '', reverse=True)
    return Response({"chat_seller_lists": chat_seller_lists_data})


@extend_schema(
    tags=["provider chat"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Api_provider_Chat_All_Messages(request):
    to_user_slug = request.GET.get('to_user')
    dialog_id = request.GET.get('dialog_id')
    dialog_slug = request.GET.get('dialog_slug')
    page_number = request.GET.get('page', 1)
    per_page = 20

    if not any([to_user_slug, dialog_id, dialog_slug]):
        return Response({'error': 'Please provide to_user, dialog_id, or dialog_slug'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        current_user = request.user
        dialog = None
        if dialog_slug:
            dialog = get_object_or_404(Dialog, slug=dialog_slug)
        elif dialog_id:
            dialog = get_object_or_404(Dialog, id=dialog_id)
        elif to_user_slug:
            try:
                to_user = User.objects.get(slug=to_user_slug)
            except User.DoesNotExist:
                return Response({'error': "User not found."}, status=status.HTTP_404_NOT_FOUND)

            dialog = Dialog.objects.filter(
                Q(provider=current_user, customer=to_user) |
                Q(provider=to_user, customer=current_user)
            ).first()

        if not dialog:
            return Response({'error': 'No chat dialog found.', 'status': 'failed'}, status=status.HTTP_404_NOT_FOUND)

        if current_user != dialog.provider and current_user != dialog.customer:
            return Response({'error': 'You do not have permission to view this chat.'}, status=status.HTTP_403_FORBIDDEN)
        Message.objects.filter(dialog=dialog, read=False).exclude(sender=current_user).update(read=True)
        other_user = dialog.provider if dialog.customer == current_user else dialog.customer
        messages_queryset = Message.objects.filter(dialog=dialog)\
            .exclude(deleted_by=current_user)\
            .select_related('sender', 'file')\
            .order_by('-created_at')
        
        paginator = Paginator(messages_queryset, per_page)
        try:
            paginated_messages = paginator.page(page_number)
        except EmptyPage:
            paginated_messages = []

        messages_serialized = []
        for msg in reversed(paginated_messages.object_list):
            sender_image_url = None
            if msg.sender.image and hasattr(msg.sender.image, 'url'):
                    sender_image_url = request.build_absolute_uri(msg.sender.image.url)

            attachment_url = None
            if msg.file:
                try:
                    if hasattr(msg.file, 'file') and msg.file.file:
                        attachment_url = request.build_absolute_uri(msg.file.file.url)
                    elif hasattr(msg.file, 'url'):
                        attachment_url = request.build_absolute_uri(msg.file.url)
                except Exception:
                    attachment_url = None

            messages_serialized.append({
                'id': str(msg.id),
                'from_user': msg.sender.slug,
                'to_user': other_user.slug,
                'message': msg.content,
                'message_type': msg.message_type,
                'attachment': attachment_url,
                'image_url': attachment_url if msg.message_type == Message.IMAGE else None,
                'created_at': msg.created_at.isoformat(),
                'updated_at': msg.updated_at.isoformat(),
                'date_human_readable': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_read': msg.read,
                'is_me': msg.sender == current_user,
                'is_starred': msg.starred_by.filter(id=current_user.id).exists(),
                'sender_username': msg.sender.get_full_name() or msg.sender.email,
                'sender_profile_image': sender_image_url,
            })

        response_data = {
            'messages': {
                'current_page': int(page_number),
                'data': messages_serialized,
                'last_page': paginator.num_pages,
                'total': paginator.count,
                'has_next': paginated_messages.has_next() if hasattr(paginated_messages, 'has_next') else False,
                'has_previous': paginated_messages.has_previous() if hasattr(paginated_messages, 'has_previous') else False,
            },
            'dialog_id': str(dialog.id),
            'dialog_slug': dialog.slug,
            'other_user_status': {
                    'is_online': other_user.user_online() if hasattr(other_user, 'user_online') else False,
                    'last_seen': other_user.last_activity.isoformat() if hasattr(other_user, 'last_activity') and other_user.last_activity else None
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}", exc_info=True)
        return Response({'error': 'Failed to load messages', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["provider chat"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def provider_send_Messages(request):
    logger.info(f"--- Save Chat Message API Called by {request.user.email} ---")
    
    dialog_slug = request.data.get('dialog_slug')
    sender_slug = request.data.get('sender_slug')
    text = request.data.get('text', '')
    message_type = request.data.get('message_type', 'text')
    uploaded_file_obj = request.FILES.get('file')

    if not dialog_slug:
        return Response({"error": "dialog_slug is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not text and not uploaded_file_obj:
        return Response({"error": "Message content (text or file) is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sender = request.user
        if sender_slug and sender.slug != sender_slug:
            logger.warning(f"User {request.user.slug} tried to send message as {sender_slug}")
            return Response({"error": "Identity mismatch"}, status=status.HTTP_403_FORBIDDEN)

        dialog = Dialog.objects.filter(slug=dialog_slug).first()
        if not dialog:
            dialog = Dialog.objects.filter(id=dialog_slug).first()
        
        if not dialog:
            return Response({"error": "Dialog not found"}, status=status.HTTP_404_NOT_FOUND)

        if sender not in [dialog.provider, dialog.customer]:
            return Response({"error": "You are not authorized for this chat."}, status=status.HTTP_403_FORBIDDEN)

        file_instance = None
        file_url_str = None

        if uploaded_file_obj:
            try:
                file_instance = UploadedFile.objects.create(
                    file=uploaded_file_obj,
                    uploaded_by=sender,
                )
                if hasattr(file_instance.file, 'url'):
                    file_url_str = request.build_absolute_uri(file_instance.file.url)
                    
            except Exception as e:
                logger.error(f"Failed to save UploadedFile: {str(e)}")
                return Response({"error": "Failed to upload file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        new_message = Message.objects.create(
            dialog=dialog,
            sender=sender,
            content=text,
            message_type=message_type,
            file=file_instance,
            read=False
        )

        logger.info(f"Message {new_message.id} created successfully in DB")

        try:
            db = firestore.client()
            
            firestore_data = {
                'text': text,
                'sender_uid': sender.firebase_uid,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'message_type': message_type,
                'db_message_id': str(new_message.id),
                'is_read': False
            }

            if file_url_str:
                firestore_data['attachment'] = file_url_str
                firestore_data['image_url'] = file_url_str 

            chat_doc_id = str(dialog.id)
            db.collection('chats').document(chat_doc_id).collection('messages').add(firestore_data)
            db.collection('chats').document(chat_doc_id).set({
                'last_message': text if text else ("Attachment" if file_instance else ""),
                'last_message_time': firestore.SERVER_TIMESTAMP,
                'last_sender_uid': sender.firebase_uid,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'dialog_id': str(dialog.id),
                'dialog_slug': dialog.slug,
                'job_slug': dialog.job.slug if dialog.job else ''
            }, merge=True)

        except Exception as firestore_error:
            logger.error(f"Failed to sync message to Firestore: {firestore_error}")

        recipient = dialog.provider if sender == dialog.customer else dialog.customer
        notification_body = text if text else "Sent an attachment"
        
        send_chat_notification(
            sender=sender,
            receiver=recipient,
            message_text=notification_body,
            dialog_id=dialog.id
        )

        return Response({
            "success": True,
            "message": "Message sent successfully",
            "data": {
                "message_id": str(new_message.id),
                "dialog_id": str(dialog.id),
                "file_url": file_url_str
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error in SaveChatMessageAPI: {str(e)}", exc_info=True)
        return Response({"error": "An unexpected server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=["provider chat"])
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def provider_delete_specific_chat(request, dialog_id):
    """
    API endpoint to delete a specific chat dialog from both Django SQL and Firestore.
    """
    user = request.user
    dialog = get_object_or_404(Dialog, id=dialog_id)

    if dialog.provider != user :
        return Response(
            {'error': "You do not have permission to delete this chat."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        db = firestore.client()
        chat_ref = db.collection('chats').document(str(dialog.id))
        chat_ref.delete()
        batch = db.batch()
        messages = chat_ref.collection('messages').limit(500).stream()
        for msg in messages:
            batch.delete(msg.reference)
        batch.commit()
        dialog.delete()

        logger.info(f"Chat {dialog_id} deleted by user {user.id}")

        return Response({
            'message': 'Chat deleted successfully from both Database and Firestore.',
            'dialog_id': dialog_id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error deleting chat {dialog_id}: {str(e)}")
        return Response(
            {'error': 'Failed to delete chat.', 'details': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )