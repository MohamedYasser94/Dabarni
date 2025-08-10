
from django import forms
from django.contrib.auth import get_user_model

from core.models.blog import BlogServices, BlogCategories, CommonTags, BlogArticle, BlogArticleTranslate

User = get_user_model()


class AdminBlogCategoriesForm(forms.ModelForm):
    category_id = forms.IntegerField(required=False)

    class Meta:
        model = BlogCategories
        fields = '__all__'


class AdminCommonTagsForm(forms.ModelForm):
    class Meta:
        model = CommonTags
        fields = '__all__'


class AdminBlogArticleTagsForm(forms.ModelForm):
    category_id = forms.IntegerField(required=False)

    class Meta:
        model = CommonTags
        fields = '__all__'
        exclude = ['tag_status']


class AdminBlogServicesForm(forms.ModelForm):
    category_id = forms.IntegerField(required=False)


    class Meta:
        model = BlogServices
        fields = '__all__'


class AdminBlogArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=CommonTags.objects.filter(status='Active') )
    category = forms.ModelChoiceField(queryset=BlogCategories.objects.filter(status='Active'))

    class Meta:
        model = BlogArticle
        fields = '__all__'
        exclude = ['slug', 'code', ]


class AdminBlogArticleTranslateForm(forms.ModelForm):


    class Meta:
        model = BlogArticleTranslate
        fields = '__all__'
        exclude = ['slug', 'code', ]


