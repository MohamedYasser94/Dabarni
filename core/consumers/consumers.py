# import json
# import logging
#
# from .message_types import MessageTypes, OutgoingEventNewTextMessage, OutgoingEventMessageIdCreated
# from .db_operations import get_dialog_by_id, save_message, mark_messages_as_read
#
# logger = logging.getLogger(__name__)
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope.get('user')
#         self.dialog_id = self.scope['url_route']['kwargs']['dialog_id']
#         logger.info(f"User {self.user} connecting to dialog {self.dialog_id}")
#
#         if not self.user or not self.user.is_authenticated:
#             logger.warning(f"Unauthenticated user attempted to connect to dialog {self.dialog_id}")
#             await self.close(code=4001)  # Use standard WebSocket close code for authentication failure
#             return
#
#         self.dialog = await get_dialog_by_id(self.dialog_id)
#
#         if self.dialog is None or self.user not in [self.dialog.provider, self.dialog.customer]:
#             logger.warning(f"User {self.user} not authorized for dialog {self.dialog_id}")
#             await self.close(code=4003)  # Use standard WebSocket close code for authorization failure
#             return
#
#         self.dialog_group_name = self.dialog.group_name
#         logger.info(f"Joining group: {self.dialog_group_name}")
#
#         await self.channel_layer.group_add(self.dialog_group_name, self.channel_name)
#         await self.accept()
#
#         await self.set_user_online_status(is_online=True)
#         await mark_messages_as_read(self.dialog, self.user)
#
#     async def disconnect(self, close_code):
#         if self.user and self.user.is_authenticated:
#             await self.set_user_online_status(is_online=False)
#
#         if hasattr(self, 'dialog_group_name'):
#             await self.channel_layer.group_discard(self.dialog_group_name, self.channel_name)
#         logger.info(f"User {self.user} disconnected from dialog {self.dialog_id} with code {close_code}")
#
#     async def receive(self, text_data):
#         try:
#             data = json.loads(text_data)
#             msg_type = data.get('msg_type')
#             logger.debug(f"Received message: {data}")
#
#             if msg_type == MessageTypes.TextMessage:
#                 await self.handle_new_message(data)
#             else:
#                 logger.warning(f"Unknown message type: {msg_type}")
#         except json.JSONDecodeError as e:
#             logger.error(f"Failed to parse WebSocket message: {str(e)}")
#             await self.send(text_data=json.dumps({
#                 "msg_type": "error",
#                 "message": "Invalid message format"
#             }))
#
#     async def handle_new_message(self, data: dict):
#         text = data.get('text', '')
#         random_id = data.get('random_id')
#         logger.info(f"Handling new message: text={text}, random_id={random_id}, sender={self.user}")
#
#         try:
#             if not text:
#                 logger.warning("Empty message text received")
#                 return
#
#             message_obj = await save_message(dialog=self.dialog, sender=self.user, text=text)
#             logger.info(f"Message saved successfully: ID={message_obj.id}, Dialog={self.dialog.id}")
#
#             await self.channel_layer.send(self.channel_name, {
#                 "type": "message_id_created",
#                 "event": OutgoingEventMessageIdCreated(random_id=random_id, db_id=message_obj.id).to_json()
#             })
#
#             await self.channel_layer.group_send(
#                 self.dialog_group_name,
#                 {
#                     "type": "new_text_message",
#                     "event": OutgoingEventNewTextMessage(
#                         random_id=random_id,
#                         text=text,
#                         sender=str(self.user.pk),
#                         receiver=str(self.dialog.provider.pk if self.user == self.dialog.customer else self.dialog.customer.pk),
#                         sender_username=self.user.get_full_name()
#                     ).to_json()
#                 }
#             )
#         except Exception as e:
#             logger.error(f"Error handling new message: {str(e)}", exc_info=True)
#             await self.send(text_data=json.dumps({
#                 "msg_type": "error",
#                 "message": "Failed to save message"
#             }))
#
#     async def new_text_message(self, event):
#         await self.send(text_data=event['event'])
#
#     async def message_id_created(self, event):
#         await self.send(text_data=event['event'])
#
#     async def user_status_update(self, event):
#         await self.send(text_data=json.dumps(event['event']))
#
#     @database_sync_to_async
#     def set_user_online_status(self, is_online: bool):
#         status = 'Active' if is_online else 'Inactive'
#         self.user.is_online = status
#         self.user.save(update_fields=['is_online'])
#         logger.info(f"User {self.user} status updated to {status}")
#
#         from asgiref.sync import async_to_sync
#         from channels.layers import get_channel_layer
#         channel_layer = get_channel_layer()
#
#         if channel_layer:
#             async_to_sync(channel_layer.group_send)(
#                 self.dialog_group_name,
#                 {
#                     "type": "user_status_update",
#                     "event": {
#                         "msg_type": 5,
#                         "user_id": str(self.user.pk),
#                         "status": status,
#                     }
#                 }
#             )