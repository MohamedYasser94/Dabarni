
from django import forms
from django.contrib.auth import get_user_model


from apps.classified.models.models import JobCategories

User = get_user_model()


class AdminJobCategoryForm(forms.ModelForm):

    class Meta:
        model = JobCategories
        fields = '__all__'
