from django.utils.crypto import get_random_string
from django.utils import timezone
import threading
from django.core.mail import EmailMessage

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        EmailThread(email).start()

def handle_email_otp_sending(user):
    """
    Service function to handle Email OTP generation and saving logic.
    Returns: (success: bool, result: any)
    """
    otp_code = get_random_string(6, allowed_chars="0123456789")
    user.email_verification_otp = otp_code
    user.email_verification_otp_created_at = timezone.now()
    user.save(update_fields=['email_verification_otp', 'email_verification_otp_created_at'])

    return True, otp_code