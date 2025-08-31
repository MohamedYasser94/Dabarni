from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify

User = get_user_model()

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    hire_date = models.DateField()
    code = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Employee-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Employee, self).save(*args, **kwargs)