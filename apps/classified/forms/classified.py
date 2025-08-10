
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.classified.models.classified import *

User = get_user_model()


class AdminClassifiedCategoryForm(forms.ModelForm):

    class Meta:
        model = ClassifiedCategories
        fields = '__all__'


class AdminClassifiedLocationForm(forms.ModelForm):

    class Meta:
        model = ClassifiedLocation
        fields = '__all__'


class AdminClassifiedAdForm(forms.ModelForm):

    class Meta:
        model = ClassifiedAd
        fields = '__all__'


#ClassifiedAdItem

class AdminClassifiedAdItemForm(forms.ModelForm):

    class Meta:
        model = ClassifiedAdItem
        fields = '__all__'

#ClassifiedMedia
class AdminClassifiedMediaForm(forms.ModelForm):

    class Meta:
        model = ClassifiedMedia
        fields = '__all__'


#AdAttribute
class AdminAdAttributeForm(forms.ModelForm):

    class Meta:
        model = AdAttribute
        fields = '__all__'

#PromotedClassifiedAd
class AdminPromotedClassifiedAdForm(forms.ModelForm):

    class Meta:
        model = PromotedClassifiedAd
        fields = '__all__'

#Favorite
class AdminFavoriteForm(forms.ModelForm):

    class Meta:
        model = Favorite
        fields = '__all__'


#ClassifiedReview
class AdminClassifiedReviewForm(forms.ModelForm):

    class Meta:
        model = ClassifiedReview
        fields = '__all__'


#USerSearch
class AdminUserSearchForm(forms.ModelForm):

    class Meta:
        model = UserSearch
        fields = '__all__'

#UserSavedSearch
class AdminUserSavedSearchForm(forms.ModelForm):

    class Meta:
        model = UserSavedSearch
        fields = '__all__'

#Commercials
class AdminCommercialsForm(forms.ModelForm):

    class Meta:
        model = Commercials
        fields = '__all__'

