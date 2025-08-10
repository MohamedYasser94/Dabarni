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


class Currency(models.Model):
    """
    Updated Currency model to support the Flutter application's needs.
    """
    name = models.CharField(max_length=50, unique=True, default='US Dollar')

    # This is the standard 3-letter currency code (e.g., 'USD')
    currency_code = models.CharField(max_length=5, choices=Currency_List, unique=True, default='USD')

    # Added 'symbol' and 'position' fields as expected by the Flutter app
    symbol = models.CharField(max_length=5, default='$', help_text="The currency symbol (e.g., $, €, £)")
    position = models.CharField(max_length=10, choices=[('left', 'Left'), ('right', 'Right')], default='left',
                                help_text="The position of the currency symbol relative to the amount.")

    exchange = models.DecimalField(max_digits=65, decimal_places=2, default=1.00, null=True, blank=True)

    # This field is used to identify the single default currency for the app.
    # The unique=True constraint ensures only one currency can be the default.
    default = models.CharField(max_length=20, choices=Active_Status, default='Inactive', unique=True, null=True,
                               blank=True)

    status = models.CharField(max_length=20, choices=Active_Status, default='Active')

    # This is a unique internal code for your reference
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate a unique internal code and slug if they don't exist
        if not self.code:
            self.code = f'CUR-{get_random_string(8).upper()}'
        if not self.slug:
            self.slug = slugify(self.code)

        # Ensure that if a currency is set as default, it's also active
        if self.default == 'Active':
            self.status = 'Active'

        super(Currency, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Currencies"








class Country(models.Model):
    name = models.CharField(max_length=100,choices=Country_List, default='Egypt')
    country_code = models.CharField(max_length=5, default='kw', null=True, blank=True)
    capital = models.CharField(max_length=100, default='Cairo', null=True, blank=True)
    calling_code = models.CharField(max_length=10, default='+965',choices=Calling_Code, null=True, blank=True)
    flag_emoji = models.CharField(max_length=250,default='', choices=Flag_Emoji,null=True, blank=True)
    flag_svg = models.CharField(max_length=100, default='https://restcountries.com/data/egy.svg', null=True, blank=True)
    flag_svg_path = models.CharField(max_length=100, default='https://restcountries.com/data/egy.svg', null=True, blank=True)
    nationality = models.CharField(max_length=100, default='Egyptian', null=True, blank=True)
    image = models.ImageField(upload_to='images/country/%Y/%m/%d', default='images/lang/en-gb.png', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'Country-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Country, self).save(*args, **kwargs)




class Governorates(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, choices=Governorates_List, default='Cairo')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'Governorates-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Governorates, self).save(*args, **kwargs)


class City(models.Model):
    governorates = models.ForeignKey(Governorates, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default='Qena')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'City-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(City, self).save(*args, **kwargs)


class Area(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30, default='Qena')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'Area-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Area, self).save(*args, **kwargs)
