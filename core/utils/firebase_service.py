import logging
from typing import Any, Dict
from uuid import uuid4

import firebase_admin
from allauth.conftest import auth_client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from firebase_admin import firestore

User = get_user_model()



firestore_client = firestore.client(app=firebase_admin.get_app())

logger = logging.getLogger(__name__)


def cached(func):
    def wrapper(*args, **kwargs):
        user = kwargs.get('user')
        key = 'token_' + str(user.id)
        token = cache.get(key)
        if token is None:
            token = func(*args, **kwargs)
            cache.set(key, token, timeout=60 * 60) # 1 hour
        return token

    return wrapper

class FirebaseService:
  @staticmethod
  @cached
  def get_custom_token_for_user(user: User):
    auth_claims = {
      'uid': user.id,
    }
    return auth_client.create_custom_token(uid=user.id, developer_claims=auth_claims)

  @staticmethod
  def send_notification_to_user(user: User, message: Dict[str, Any]):
    msg_id = str(uuid4())
    notification_ref = firestore_client.collection(u'app-notifications') \
      .document(u'{}'.format(user.id)).collection("user-notifications").document(u'{}'.format(msg_id))

    notification_ref.set({
      u'message': message,
      'id': msg_id
    })
    logger.info(u'Notification sent to user {}'.format(user.id))