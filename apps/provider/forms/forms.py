
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.classified.models.models import JobProvider

User = get_user_model()


class AdminJobProviderForm(forms.ModelForm):
    class Meta:
        model = JobProvider
        fields = '__all__'