# In your_app/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.classified.models.ticket import ServiceReview


@receiver(post_save, sender=ServiceReview)
def update_rating_on_save(sender, instance, **kwargs):
    """
    Signal handler to update the job's average rating when a review is saved.
    """
    instance.job.update_rating()

@receiver(post_delete, sender=ServiceReview)
def update_rating_on_delete(sender, instance, **kwargs):
    """
    Signal handler to update the job's average rating when a review is deleted.
    """
    instance.job.update_rating()