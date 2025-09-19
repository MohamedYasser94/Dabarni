
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import request
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


from apps.classified.models.ticket import *
from core.models.localization import *
from user.forms.forms import UserSignUpForm

User = get_user_model()


class AdminSupportTicketForm(forms.ModelForm):

    class Meta:
        model = SupportTicket
        fields = '__all__'
        exclude = ['code', 'slug']



class AdminTicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        # FIX: Explicitly define only the fields the user should fill.
        # This will make the 'message' field render correctly.
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your reply here...',
                'rows': 3, # Adjusted for a cleaner look
            }),
        }



class AdminServiceReviewForm(forms.ModelForm):


    class Meta:
        model = ServiceReview
        fields = '__all__'


class AdminReportForm(forms.ModelForm):


    class Meta:
        model = Report
        fields = '__all__'
        exclude = ['code','slug']

class AdminReportMessageForm(forms.ModelForm):



    class Meta:
        model = ReportMessage
        fields = '__all__'
        exclude = ['product']





