# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import Active_Status, Banners_Position






class PrivacyPolicy(models.Model):
    status = models.CharField(max_length=30, choices=Active_Status, null=True, blank=True, default="Active")
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name="Title")
    description = models.TextField(max_length=1500, null=True, blank=True)
    author = models.CharField(max_length=150, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home:FrontPrivacyPolicyDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PrivacyPolicy-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PrivacyPolicy, self).save(*args, **kwargs)

class TermsOfService(models.Model):
    status = models.CharField(max_length=30, choices=Active_Status, null=True,blank=True,default="Active")
    title = models.CharField(max_length=150,  null=True,blank=True, verbose_name="Title")
    description = models.TextField(max_length=1500,  null=True,blank=True )
    author = models.CharField(max_length=150, null=True,blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('home:FrontTermsOfServiceDetails', kwargs={'slug': self.slug})
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TermsOfService-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TermsOfService, self).save(*args, **kwargs)




