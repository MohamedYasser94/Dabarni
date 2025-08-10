from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.classified.forms.classified import AdminClassifiedCategoryForm
from apps.classified.forms.job import AdminJobCategoryForm
from apps.classified.models.classified import ClassifiedCategories
from apps.classified.models.job import JobCategories
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()


##########################      Blog Category Admin            ################################

@authenticated_staff
@staff_only
def AdminClassifiedCategoriesList(request):
    categories = ClassifiedCategories.objects.all()
    if request.method == "POST":
        category_form = AdminClassifiedCategoryForm(request.POST or None, request.FILES or None)
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            image = request.FILES.get('image')
            try:
                parent_id = JobCategories.objects.get(id=parent)
            except Exception as e:
                parent_id = None
            category_object = ClassifiedCategories(title=title, keyword=keyword, parent=parent_id,
                                            image=image, )
            category_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoriesList'))
        else:
            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')
    context = {
        'categories': categories,
        'category_form': AdminClassifiedCategoryForm(),
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/admin.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedCategoryUpdate(request, slug):
    category = ClassifiedCategories.objects.get(slug=slug)

    if request.method == "POST":
        category_form = AdminClassifiedCategoryForm(request.POST or None, request.FILES or None)

        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            image = request.FILES.get('image')
            try:
                parent_id = JobCategories.objects.get(id=parent)
            except Exception as e:
                parent_id = None
            category.title = title
            category.keyword = keyword
            category.parent = parent_id
            if image:
                category.image = image
            category.save()
            messages.success(request, _("Category Update Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoriesList'))
        else:
            messages.error(request, _("Category Not Update , Please Try Again"), extra_tags='Category')

    context = {
        'category': category,
        'category_form': AdminClassifiedCategoryForm(instance=category),
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/admin.html', context)


@authenticated_staff
@staff_only
def AdminClassifiedCategoryDelete(request, slug):
    category = ClassifiedCategories.objects.get(slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('classified:AdminClassifiedCategoriesList'))
    context = {
        'category': category,
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/delete.html', context)
