import json

from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify
from helper.modelHelper import *


# Create your models here.

from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
import json


class Language(models.Model):
    """
    Model to store language settings, including direction (RTL/LTR)
    and the JSON translation data.
    """
    name = models.CharField(max_length=50, default='ar')
    name_in_english = models.CharField(max_length=50, default='ar', help_text="The name of the language in English.")
    code = models.CharField(max_length=10, default='ar', help_text="Language code, e.g., 'en', 'ar'.")
    country_code = models.CharField(max_length=10, default='eg', help_text="Country code, e.g., 'US', 'SA'.")
    direction = models.CharField(max_length=3, choices=[('ltr', 'LTR'), ('rtl', 'RTL')], default='ltr')
    image = models.FileField(upload_to='languages/', null=True, blank=True, help_text="Upload flag image.")

    # REMOVED the old file_name field
    # file_name = models.FileField(upload_to='languages/json/', ...)

    default = models.CharField(max_length=20, default='Inactive')  # Changed default to 'Inactive' to be safer
    translations = models.JSONField(default=dict, blank=True, help_text="Add translations as key-value pairs")
    status = models.CharField(max_length=20, default='Active')
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            random = get_random_string(5).upper()
            # Ensure slug is unique if multiple languages have similar random strings initially
            potential_slug = slugify(f"{self.name}-{random}")
            if Language.objects.filter(slug=potential_slug).exists():
                random = get_random_string(5).upper()
                potential_slug = slugify(f"{self.name}-{random}")
            self.slug = potential_slug

        # Ensure only one language can be default at a time
        if self.default == 'Active':
            Language.objects.filter(default='Active').exclude(pk=self.pk).update(default='Inactive')
            self.status = 'Active'  # A default language must be active

        super().save(*args, **kwargs)

    def get_translations(self):
        """Returns the translations from the JSONField."""
        return self.translations

    class Meta:
        verbose_name_plural = "Languages"








