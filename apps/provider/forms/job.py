
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _



from apps.classified.models.job import *


User = get_user_model()


class AdminJobCategoryForm(forms.ModelForm):

    class Meta:
        model = JobCategories
        fields = '__all__'


class AdminJobLocationForm(forms.ModelForm):
    class Meta:
        model = JobLocation
        fields = '__all__'
class AdminJobProviderForm(forms.ModelForm):
    class Meta:
        model = JobProvider
        fields = '__all__'

class AdminJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = '__all__'


class AdminJobRequirementForm(forms.ModelForm):
    class Meta:
        model = JobRequirement
        fields = '__all__'


class AdminJobBenefitForm(forms.ModelForm):
    class Meta:
        model = JobBenefit
        fields = '__all__'


class AdminJobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        fields = '__all__'


class AdminJobRequestDocumentForm(forms.ModelForm):
    class Meta:
        model = JobRequestDocument
        fields = '__all__'


class AdminJobMediaForm(forms.ModelForm):
    class Meta:
        model = JobMedia
        fields = '__all__'


class AdminJobReviewForm(forms.ModelForm):
    class Meta:
        model = JobReview
        fields = '__all__'

class JobRequestForm(forms.ModelForm):
    class Meta:
        model = JobRequest
        
       
        fields = ['message', 'attachment']
        
     
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Write a message to the provider (optional)...')
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        
      
        labels = {
            'message': _('Message'),
            'attachment': _('Attach File'),
        }       



