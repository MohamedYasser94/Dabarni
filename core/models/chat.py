# In core/models/chat.py

import uuid
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils.crypto import get_random_string
from slugify import slugify


# It's assumed you have a 'Job' model somewhere in your project.
# from jobs.models import Job # <--- IMPORTANT: Import your actual Job model here

# This utility model remains useful for handling file attachments in messages.
class UploadedFile(models.Model):
    file = models.FileField(upload_to='chat_files/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    @property
    def url(self):
        return self.file.url if self.file else None

class Dialog(models.Model):
    """
    Represents a one-to-one conversation between a Job Provider and a Customer.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey('classified.Job', on_delete=models.CASCADE, related_name="dialogs", null=True, blank=True)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="provider_dialogs")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_dialogs")
    code = models.CharField(max_length=255, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'customer')
        ordering = ('-created_at',)

    def __str__(self):
        return f"Dialog between {self.provider.email} and {self.customer.email}"

    @property
    def group_name(self):
        return f"dialog_{self.id}"

    def get_shared_media(self):
        """
        Returns a queryset of all UploadedFile objects shared in this dialog.
        """
        return UploadedFile.objects.filter(message__dialog=self).distinct()

    def get_shared_links(self):
        """
        Returns a list of all links shared in this dialog's messages.
        """
        import re
        url_regex = r'(https?://[^\s]+)'
        links = []
        for msg in self.messages.all():
            links += re.findall(url_regex, msg.content or "")
        return links

    def save(self , *args, **kwargs):

        if not self.code and not self.slug:
            code = f'Dialog-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Dialog, self).save()

class Message(models.Model):
    """
    Represents a single message within a Dialog.
    Supports text, file, image, audio, and video messages.
    Allows starring, deleting, and tracks read status.
    """
    TEXT = 'text'
    FILE = 'file'
    IMAGE = 'image'
    AUDIO = 'audio'
    VIDEO = 'video'
    MESSAGE_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (FILE, 'File'),
        (IMAGE, 'Image'),
        (AUDIO, 'Audio'),
        (VIDEO, 'Video'),
    ]

    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField(blank=True)
    file = models.ForeignKey(UploadedFile, on_delete=models.SET_NULL, null=True, blank=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default=TEXT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    starred_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="starred_messages", blank=True)
    deleted_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="deleted_messages", blank=True)
    # Optionally, add reactions, edit history, etc.

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"

    @property
    def is_file(self):
        return self.message_type in [self.FILE, self.IMAGE, self.AUDIO, self.VIDEO] and self.file is not None

    @property
    def file_url(self):
        return self.file.url if self.file else None

    @property
    def is_starred(self):
        return self.starred_by.exists()

    @property
    def is_deleted(self):
        return self.deleted_by.exists()

    def as_dict(self):
        """
        Serialize message for API/JSON.
        """
        return {
            'id': str(self.id),
            'dialog_id': str(self.dialog_id),
            'sender': self.sender.id,
            'sender_username': self.sender.get_full_name(),
            'content': self.content,
            'message_type': self.message_type,
            'file_url': self.file.url if self.file else None,
            'created_at': self.created_at.isoformat(),
            'read': self.read,
            'starred': [u.id for u in self.starred_by.all()],
            'deleted': [u.id for u in self.deleted_by.all()],
        }