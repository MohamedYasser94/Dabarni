
from django import forms
from django.contrib.auth import get_user_model

from apps.customer.models.models import Employee

User = get_user_model()


class AdminEmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = '__all__'


