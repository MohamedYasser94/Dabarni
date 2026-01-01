import logging
from firebase_admin import messaging
from django.conf import settings
from core.models.notifications import MobileNotification

logger = logging.getLogger(__name__)

def send_fcm_notification(user, title, body, data=None, notification_type="general"):
    fcm_token = getattr(user, 'fcm_token', None)

    if not fcm_token or str(fcm_token).strip() == '':
        logger.warning(f"FCM: User {user.email} (ID: {user.id}) has no FCM token. Notification NOT sent.")
        return False

    if data is None:
        data = {}

    if 'type' not in data:
        data['type'] = notification_type

    clean_data = {}
    for k, v in data.items():
        if v is not None:
            clean_data[str(k)] = str(v)

    try:
        notification_obj = messaging.Notification(
            title=title,
            body=body,
        )

        message = messaging.Message(
            notification=notification_obj,
            token=fcm_token,
            data=clean_data
        )

        response = messaging.send(message)
        logger.info(f"FCM: Sent successfully to {user.email}. Type: {clean_data.get('type')}")
        return True

    except Exception as e:
        logger.error(f"FCM: Failed to send to {user.email}. Error: {e}", exc_info=True)
        return False

def send_chat_notification(sender, receiver, message_text, dialog_id=None):
    sender_name = sender.get_full_name() or "User"
    title = f"New message from {sender_name}"
    body = message_text if len(message_text) < 100 else f"{message_text[:97]}..."

    data_payload = {
        "type": "chat_message",
        "sender_id": str(sender.id),
        "sender_slug": str(getattr(sender, 'slug', '')),
        "dialog_id": str(dialog_id) if dialog_id else "",
        "click_action": "FLUTTER_NOTIFICATION_CLICK"
    }
    return send_fcm_notification(receiver, title, body, data=data_payload, notification_type="chat_message")

def send_general_notification(receiver, title, body, notification_type="general", extra_data=None):
    if extra_data is None:
        extra_data = {}
        
    data_payload = {
        "type": notification_type,
        **extra_data
    }
    return send_fcm_notification(receiver, title, body, data=data_payload, notification_type=notification_type)