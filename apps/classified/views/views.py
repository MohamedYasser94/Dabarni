from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.classified.forms.forms import AdminJobCategoryForm
from apps.classified.models.models import JobCategories
from helper.commonHelper import *
from helper.decorators import *

# Assumption: Your models are in one of these locations. Adjust as needed.

User = get_user_model()


########################## Classified Category Admin ################################
# Note: These are the functions you provided as a reference.

@authenticated_staff
@staff_only
def AdminJobCategoriesList(request):
    categories = JobCategories.objects.all()
    if request.method == "POST":
        # This view combines List and Create functionality.
        category_form = AdminJobCategoryForm(request.POST or None, request.FILES or None)
        if category_form:
            title = request.POST.get('title')

            image = request.FILES.get('image')


            category_object = JobCategories(
                title=title,

                image=image,

            )
            category_object.save()

            messages.success(request, _("Category Added Successfully"), extra_tags='Category')
            return HttpResponseRedirect(reverse_lazy('classified:AdminJobCategoriesList'))
        else:
            messages.error(request, _("Category Not Added, Please Try Again"), extra_tags='Category')

    context = {
        'categories': categories,
        'category_form': AdminJobCategoryForm(),
        'current_page': _('Categories')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/admin.html', context)


@authenticated_staff
@staff_only
def AdminJobCategoryUpdate(request, slug):
    category = JobCategories.objects.get(slug=slug)
    category_form = AdminJobCategoryForm(request.POST or None, request.FILES or None, instance=category)

    if request.method == "POST":
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            image = request.FILES.get('image')
            job_category = request.POST.get('job_category')
            parent = request.POST.get('parent')
            status = request.POST.get('status')

            if parent:
                parent_category = JobCategories.objects.get(id=parent)
                if parent_category.slug == slug:
                    messages.error(request, _("Parent category cannot be the same as the current category."), extra_tags='Category')
                    return HttpResponseRedirect(reverse_lazy('provider:AdminClassifiedCategoryUpdate', kwargs={'slug': slug}))
            else:
                parent_category = None


            category_object = JobCategories.objects.get(slug=slug)
            category_object.title = title
            category_object.keyword = keyword
            category_object.image = image
            category_object.job_category = job_category
            category_object.parent = parent_category
            category_object.status = status
            category_object.save()
            messages.success(request, _("Category Updated Successfully"), extra_tags='Category')
            return HttpResponseRedirect(reverse_lazy('provider:AdminJobCategoriesList'))
        else:
            messages.error(request, _("Category Not Updated, Please Try Again"), extra_tags='Category')

    context = {
        'category': category,
        'category_form': category_form,
        'current_page': _('Categories')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/category/update.html', context)


@authenticated_staff
@staff_only
def AdminJobCategoryDelete(request, slug):
    try:
        category = JobCategories.objects.get(slug=slug)
    except JobCategories.DoesNotExist:
        messages.error(request, _("Category not found"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('classified:AdminJobCategoriesList'))
    
    if request.method == "POST":
        category_name = category.title
        category.delete()
        messages.success(request, _(f"Category '{category_name}' deleted successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('classified:AdminJobCategoriesList'))
    
    messages.error(request, _("Invalid request method"), extra_tags='Category')
    return HttpResponseRedirect(reverse_lazy('classified:AdminJobCategoriesList'))
