# # in core/db_operations.py
# import logging
#
# from django.contrib.auth import get_user_model
# from django.db.models import Q
# from typing import Optional
# from core.models.chat import Dialog, Message, UploadedFile
#
# User = get_user_model()
# logger = logging.getLogger(__name__)
#
# @database_sync_to_async
# def get_dialog_by_id(dialog_id: str) -> Optional[Dialog]:
#     """
#     Fetches a dialog by its UUID.
#     """
#     try:
#         dialog = Dialog.objects.select_related('provider', 'customer').get(id=dialog_id)
#         logger.info(f"Dialog fetched: ID={dialog_id}")
#         return dialog
#     except Dialog.DoesNotExist:
#         logger.warning(f"Dialog with id {dialog_id} does not exist.")
#         return None
#     except Exception as e:
#         logger.error(f"Error fetching dialog {dialog_id}: {str(e)}")
#         raise
#
# @database_sync_to_async
# def get_or_create_dialog_between(user1: User, user2: User) -> Dialog:
#     """
#     Finds or creates a dialog between two users.
#     """
#     try:
#         # Assumes the user with position 'Provider' is the provider, otherwise falls back to user1
#         if user1.position == 'Provider':
#             provider, customer = user1, user2
#         else:
#             provider, customer = user2, user1
#
#         dialog, created = Dialog.objects.get_or_create(provider=provider, customer=customer)
#         if created:
#             logger.info(f"Created new dialog: ID={dialog.id}, Provider={provider.id}, Customer={customer.id}")
#         else:
#             logger.info(f"Retrieved existing dialog: ID={dialog.id}")
#         return dialog
#     except Exception as e:
#         logger.error(f"Error getting or creating dialog between users {user1.id} and {user2.id}: {str(e)}")
#         raise
#
# @database_sync_to_async
# def save_message(dialog: Dialog, sender: User, text: str, file_id: Optional[str] = None) -> Message:
#     """
#     Saves a new text or file message to the database.
#     """
#     try:
#         file = None
#         if file_id:
#             try:
#                 file = UploadedFile.objects.get(id=file_id)
#             except UploadedFile.DoesNotExist:
#                 logger.warning(f"UploadedFile with id {file_id} does not exist.")
#
#         message = Message.objects.create(dialog=dialog, sender=sender, content=text, file=file)
#         logger.info(f"Message saved: ID={message.id}, Dialog={dialog.id}, Sender={sender.id}")
#         return message
#     except Exception as e:
#         logger.error(f"Failed to save message: {str(e)}", exc_info=True)
#         raise
#
# @database_sync_to_async
# def mark_messages_as_read(dialog: Dialog, user: User):
#     """
#     Marks all unread messages in a dialog for a specific user as read.
#     """
#     try:
#         updated_count = Message.objects.filter(dialog=dialog, read=False).exclude(sender=user).update(read=True)
#         logger.info(f"Marked {updated_count} messages as read for user {user.id} in dialog {dialog.id}")
#     except Exception as e:
#         logger.error(f"Error marking messages as read for dialog {dialog.id}: {str(e)}")
#         raise