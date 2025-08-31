# In your_app/models.py
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, Count
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.classified.models.models import Job

User = get_user_model()

# Choices for ticket priority and status, matching what your app might need
PRIORITY_CHOICES = (
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Urgent', 'Urgent'),
)

STATUS_CHOICES = (
    ('Open', 'Open'),
    ('Closed', 'Closed'),
)


class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    description = models.TextField()
    order = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

    class Meta:
        ordering = ['-create_at']

    # FIX: Update the save method signature to accept *args and **kwargs
    def save(self, *args, **kwargs):
        # This logic generates a code and slug only when the object is first created
        if not self.code:
            code = f'SupportTicket-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)

        # Pass all original arguments and keyword arguments to the parent save method
        super(SupportTicket, self).save(*args, **kwargs)


class TicketMessage(models.Model):
    """
    Represents a single message within a support ticket.
    """
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)
    user_type = models.CharField(max_length=20, default='buyer')
    is_read = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message for Ticket #{self.ticket.id} by {self.user.username}"

    class Meta:
        ordering = ['create_at']





class Report(models.Model):
    """
    Represents a report filed by a buyer against a seller or service.
    """
    REPORT_STATUS_CHOICES = (
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
        ('Rejected', 'Rejected'),

    )
    order_slug = models.TextField(null=True, blank=True)
    service = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, related_name='reports')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    report = models.TextField()
    status = models.TextField(default='New', choices=REPORT_STATUS_CHOICES)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report #{self.id} by {self.buyer.email}"

    @property
    def report_from(self):
        return self.buyer.email

    @property
    def report_to(self):
        return self.seller.email

    def save(self , *args, **kwargs):

        if not self.code and not self.slug:
            code = f'Report-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Report, self).save()



class ReportMessage(models.Model):
    """
    Represents a single message within a report thread.
    """
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to='report_attachments/', null=True, blank=True)
    user_type = models.CharField(max_length=20, default='buyer')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for Report #{self.report.id} by {self.user.username}"