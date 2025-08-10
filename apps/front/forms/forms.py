from django import forms

from apps.front.models.models import *

User = get_user_model()


class AdminTemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = '__all__'


class AdminCategoryForm(forms.ModelForm):
    class Meta:
        model = FrontCategories
        fields = '__all__'


class AdminTagsForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = '__all__'


class AdminPagesForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = '__all__'


class AdminSectionsForm(forms.ModelForm):
    class Meta:
        model = Sections
        fields = '__all__'


class AdminMenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'


class AdminMenuItemsForm(forms.ModelForm):
    class Meta:
        model = MenuItems
        fields = '__all__'


class AdminSliderForm(forms.ModelForm):
    class Meta:
        model = Slider
        fields = '__all__'


class AdminSliderItemForm(forms.ModelForm):
    class Meta:
        model = SliderItem
        fields = '__all__'


class AdminBannerForm(forms.ModelForm):


    class Meta:
        model = Banner
        fields = '__all__'


class AdminBannerItemForm(forms.ModelForm):
    class Meta:
        model = BannerItem
        fields = '__all__'


class AdminBlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = '__all__'


class AdminBlockItemForm(forms.ModelForm):
    class Meta:
        model = BlockItem
        fields = '__all__'


class AdminTestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'


class AdminTestimonialItemForm(forms.ModelForm):
    class Meta:
        model = TestimonialItem
        fields = '__all__'