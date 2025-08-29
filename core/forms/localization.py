from django.forms import ModelForm


from core.models.localization import Language

class AdminLanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'
        exclude = ['slug', 'code']

