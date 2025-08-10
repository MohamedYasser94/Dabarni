from decimal import Decimal

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from apps.classified.forms.job import *
from apps.classified.models.job import *
from core.utils.backends import RandomPasswordGenerator
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()


##########################      Blog Category Admin            ################################

@authenticated_staff
@staff_only
def AdminJobCategoryList(request):
    categories = JobCategories.objects.all()

    if request.method == "POST":
        category_form = AdminJobCategoryForm(request.POST or None, request.FILES or None)
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            image = request.FILES.get('image')
            try:
                parent_id = JobCategories.objects.get(id=parent)
            except Exception as e:
                parent_id = None
            category_object = JobCategories(title=title, keyword=keyword, parent=parent_id,
                                            image=image, )
            category_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('job:AdminJobCategoryList'))
        else:
            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')
    context = {
        'categories': categories,
        'category_form': AdminJobCategoryForm(),
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/job/category/admin.html', context)


@authenticated_staff
@staff_only
def AdminJobCategoryCreate(request):
    if request.method == "POST":
        category_form = AdminJobCategoryForm(request.POST or None, request.FILES or None)

        title = request.POST.get('title', '').strip()
        keyword = request.POST.get('keyword', '').strip()
        parent = request.POST.get('parent')
        image = request.FILES.get('image')

        # Validation manually
        errors = []

        if not title:
            errors.append(_("Title is required."))

        if not keyword:
            errors.append(_("Keyword is required."))

        try:
            parent_id = JobCategories.objects.get(id=parent) if parent else None
        except JobCategories.DoesNotExist:
            parent_id = None
            if parent:
                errors.append(_("Selected parent category does not exist."))

        if not errors:
            category_object = JobCategories(
                title=title,
                keyword=keyword,
                parent=parent_id,
                image=image
            )
            category_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')
            return HttpResponseRedirect(reverse_lazy('job:AdminJobCategoryList'))
        else:
            for err in errors:
                messages.error(request, err, extra_tags='Category')

    context = {
        'category_form': AdminJobCategoryForm(),
        'current_page': _('Add Category'),
        'prev_Page': _('Categories'),
        'prev_Page_link': reverse_lazy('job:AdminJobCategoryList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/category/add.html', context)








@authenticated_staff
@staff_only
def AdminJobCategoryUpdate(request, slug):
    category = JobCategories.objects.get(slug=slug)


    if request.method == "POST":
        category_form = AdminJobCategoryForm(request.POST or None, request.FILES or None)

        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            color = request.POST.get('color')

            if parent == '' or parent == "''" or parent == None:
                parent_id = None
            else:
                parent_id = JobCategories.objects.get(id=parent)
            category_object = JobCategories.objects.get(id=category.id)
            category_object.title = title
            category_object.keyword = keyword
            category_object.parent = parent_id
            category_object.status = status
            if image:
                category_object.image = image
            else:
                category_object.image = category_object.image
            category_object.color = color
            category_object.save()

            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('job:AdminJobCategoryList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')

    context = {
        'category': category,

        'category_form': AdminJobCategoryForm(),
        'current_page': _('Update'),
        'prev_Page': _('Categories'),
        'prev_Page_link': reverse_lazy('job:AdminJobCategoryList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/job/category/update.html', context)


@authenticated_staff
@staff_only
def AdminJobCategoryDelete(request, slug):
    category = JobCategories.objects.get(slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('job:AdminJobCategoryList'))

##########  JobProvider  Admin #########
@authenticated_staff
@staff_only
def AdminJobProviderList(request):
    providers = JobProvider.objects.all()
    context = {
        'providers': providers,
        'current_page': _('Providers')
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/provider/admin.html', context)

# -------------------- Job Provider Create, Update, Delete --------------------
@authenticated_staff
@staff_only
def AdminJobProviderCreate(request):
    if request.method == "POST":
        provider_form = AdminJobProviderForm(request.POST or None, request.FILES or None)
        if provider_form:

            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            type = request.POST.get('type')
            description = request.POST.get('description')
            id_image = request.FILES.get('id_image')
            document_image = request.FILES.get('document_image')
            proof_image = request.FILES.get('proof_image')
            location_image = request.FILES.get('location_image')
            address_image = request.FILES.get('location_image')
            address_video = models.URLField(blank=True, null=True)
            image = request.FILES.get('image')
            number = request.POST.get('number')
            proof_number = request.POST.get('proof_number')
            id_number = request.POST.get('id_number')
            document_number = request.POST.get('document_number')
            bank_account = request.POST.get('bank_account')
            governorate = request.POST.get('governorate')
            address = request.POST.get('address')
            website = request.POST.get('website')
            latitude = models.FloatField(blank=True, null=True)
            longitude = models.FloatField(blank=True, null=True)
            data_confirmed = request.POST.get('data_confirmed')
            status = request.POST.get('status')

            # check user by email if empty create one  if exist returnn message error
            try:
                User.objects.get(email=email)
                messages.error(request, _("Email already exists, please use a different email."), extra_tags='Provider')
                return HttpResponseRedirect(reverse_lazy('job:AdminJobProviderList'))
            except User.DoesNotExist:
                # Create a new user if the email does not exist
                user = User(
                    email=email,
                    first_name=name,
                    is_active='Active',
                    access_level='Provider',
                )
                user.save()
                password = RandomPasswordGenerator()
                user.set_password(password)
                user.save()

                provider_object = JobProvider(
                    user=user,
                    name=name,
                    email=email,
                    phone=phone,
                    type=type,
                    description=description,
                    id_image=id_image,
                    document_image=document_image,
                    proof_image=proof_image,
                    location_image=location_image,
                    image=image,
                    address_image=address_image,
                    address_video=address_video,
                    number=number,
                    proof_number=proof_number,
                    id_number=id_number,
                    document_number=document_number,
                    bank_account=bank_account,
                    governorate_id=governorate if governorate else None,
                    address=address,
                    website=website,
                    latitude=latitude,
                    longitude=longitude,
                    data_confirmed=data_confirmed,
                    status=status
            )
                provider_object.save()
                messages.success(request, _("Provider Add Successfully"), extra_tags='Provider')
                return HttpResponseRedirect(reverse_lazy('job:AdminJobProviderList'))
        else:
            messages.error(request, _("Provider Not Add , Please Try Again"), extra_tags='Provider')
    else:
        provider_form = AdminJobProviderForm()

    context = {
        'provider_form': provider_form,
        'current_page': _('Add Provider'),
        'prev_Page': _('Providers'),
        'prev_Page_link': reverse_lazy('job:AdminJobProviderList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/provider/add.html', context)


@authenticated_staff
@staff_only
def AdminJobProviderUpdate(request, slug):
    provider = JobProvider.objects.get(slug=slug)

    if request.method == "POST":
        provider_form = AdminJobProviderForm(request.POST or None, request.FILES or None)

        if provider_form:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            type = request.POST.get('type')
            description = request.POST.get('description')
            id_image = request.FILES.get('id_image')
            document_image = request.FILES.get('document_image')
            proof_image = request.FILES.get('proof_image')
            location_image = request.FILES.get('location_image')
            image = request.FILES.get('image')
            number = request.POST.get('number')
            proof_number = request.POST.get('proof_number')
            id_number = request.POST.get('id_number')
            document_number = request.POST.get('document_number')
            bank_account = request.POST.get('bank_account')
            governorate = request.POST.get('governorate')
            address = request.POST.get('address')
            website = request.POST.get('website')
            data_confirmed = request.POST.get('data_confirmed')
            status = request.POST.get('status')

            provider_object = JobProvider.objects.get(id=provider.id)
            provider_object.name = name
            provider_object.email = email
            provider_object.phone = phone
            provider_object.type = type
            provider_object.description = description
            if id_image:
                provider_object.id_image = id_image
            if document_image:
                provider_object.document_image = document_image
            if proof_image:
                provider_object.proof_image = proof_image
            if location_image:
                provider_object.location_image = location_image
            if image:
                provider_object.image = image
            provider_object.number = number
            provider_object.proof_number = proof_number
            provider_object.id_number = id_number
            provider_object.document_number = document_number
            provider_object.bank_account = bank_account
            if governorate == '' or governorate == "''" or governorate == None:
                provider_object.governorate_id = None
            else:
                provider_object.governorate_id = governorate
            provider_object.address = address
            provider_object.website = website
            provider_object.data_confirmed = data_confirmed
            provider_object.status = status
            provider_object.save()
            messages.success(request, _("Provider Update Successfully"), extra_tags='Provider')
            return HttpResponseRedirect(reverse_lazy('job:AdminJobProviderList'))
        else:
            messages.error(request, _("Provider Not Update , Please Try Again"), extra_tags='Provider')

    context = {
        'provider': provider,
        'provider_form': AdminJobProviderForm(),
        'current_page': _('Update Provider'),
        'prev_Page': _('Providers'),
        'prev_Page_link': reverse_lazy('job:AdminJobProviderList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/job/provider/update.html', context)


@authenticated_staff
@staff_only
def AdminJobProviderDelete(request, slug):
    provider = JobProvider.objects.get(slug=slug)
    if request.method == "POST":
        provider.delete()
        messages.success(request, _("Provider Delete Successfully"), extra_tags='Provider')
        return HttpResponseRedirect(reverse_lazy('job:AdminJobProviderList'))


##########  Job  Admin #########
@authenticated_staff
@staff_only
def AdminJobList(request):
    jobs = Job.objects.all()
    context = {
        'jobs': jobs,
        'current_page': _('Jobs')
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/job/admin.html', context)


@authenticated_staff
@staff_only
def AdminJobCreate(request):
    if request.method == "POST":
        job_form = AdminJobForm(request.POST or None, request.FILES or None)
        requirement_form = AdminJobRequirementForm(request.POST or None, request.FILES or None)
        if job_form:
            """ Add Job """

            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category',None)
            location = request.POST.get('location',None)
            cost = request.POST.get('cost')
            cost_type = request.POST.get('cost_type')
            duration = request.POST.get('duration')
            need_requirements = request.POST.get('need_requirements')
            image = request.FILES.get('image')
            is_featured = request.POST.get('is_featured')
            negotiable = request.POST.get('negotiable')
            status= request.POST.get('status', 'Active')

            requirement_name = request.POST.getlist('[requirement_name]')
            requirement_description = request.POST.getlist('[requirement_description]')
            is_required = request.POST.getlist('[is_required]')

            print('requirement_type', request.POST)


            if category:
                category_object = JobCategories.objects.get(id=category)
            else:
                category_object = None


            if location:
                location_object = JobLocation.objects.get(id=location)
            else:
                location_object = None


            try:
                provider = JobProvider.objects.get(user=request.user)
            except JobProvider.DoesNotExist:

                user = User.objects.get(email=request.user.email)
                if user.access_level == 'Admin' or user.access_level == 'SuperAdmin':
                    provider = JobProvider(user =user,
                        name='Default Provider',
                        email=user.email,
                        phone=user.phone if hasattr(user, 'phone') else '',
                        type='Admin',
                        description='Admin Provider',
                        status=status
                    )
                    provider.save()

            job_object = Job(
                provider =provider,
                title=title,
                description=description,
                category=category_object,
                location=location_object,
                cost=cost,
                cost_type=cost_type,
                duration=duration,
                need_requirements=need_requirements,
                image=image,
                is_featured=is_featured,
                negotiable=negotiable
            )
            job_object.save()

            for  name, description, required in zip( requirement_name, requirement_description, is_required):
                if type and name:
                    job_requirement = JobRequirement(
                        classified_job=job_object,
                        requirement_name=name,
                        requirement_description=description,
                        is_required=required
                    )
                    job_requirement.save()
            messages.success(request, _("Job Add Successfully"), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('job:AdminJobList'))
        else:
            messages.error(request, _("Job Not Add , Please Try Again"), extra_tags='Job')
    else:
        job_form = AdminJobForm()
        requirement_form = AdminJobRequirementForm()

    context = {
        'job_form': job_form,
        'requirement_form': requirement_form,
        'current_page': _('Add Job'),
        'prev_Page': _('Jobs'),
        'prev_Page_link': reverse_lazy('job:AdminJobList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job/job/add.html', context)


@authenticated_staff
@staff_only
def AdminJobUpdate(request, slug):
    job = Job.objects.get(slug=slug)
    requirement = JobRequirement.objects.filter(classified_job=job)

    if request.method == "POST":
        job_form = AdminJobForm(request.POST or None, request.FILES or None)
        requirement_form = AdminJobRequirementForm(request.POST or None, request.FILES or None)

        if job_form:
            """ Update Job """
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category')
            location = request.POST.get('location')
            cost = request.POST.get('cost')
            cost_type = request.POST.get('cost_type')
            duration = request.POST.get('duration')
            need_requirements = request.POST.get('need_requirements')
            image = request.FILES.get('image')
            is_featured = request.POST.get('is_featured')
            negotiable = request.POST.get('negotiable')


            requirement_name = request.POST.getlist('[requirement_name]')
            requirement_description = request.POST.getlist('[requirement_description]')
            is_required = request.POST.getlist('[is_required]')

            print('requirement_type', request.POST)

            ## old requirements update
            requirement_slugs = request.POST.getlist('requirement_slug')
            requirement_name_old = request.POST.getlist('requirement_name_old')
            requirement_description_old = request.POST.getlist('requirement_description_old')
            is_required_old = request.POST.getlist('is_required_old')

            if category:
                try:
                    category_object = JobCategories.objects.get(id=category)
                except JobCategories.DoesNotExist:
                    category_object = None

            if location:
                try:
                    location_object = JobLocation.objects.get(id=location)
                except JobLocation.DoesNotExist:
                    location_object = None

            job_object = Job.objects.get(id=job.id)
            job_object.title = title
            job_object.description = description
            job_object.category_id = category
            job_object.location_id = location
            job_object.cost = Decimal(cost)
            job_object.cost_type = cost_type
            job_object.duration = duration
            job_object.need_requirements = need_requirements
            if image:
                job_object.image = image
            job_object.is_featured = is_featured
            job_object.negotiable = negotiable
            job_object.save()

            # Update existing requirements
            for slug, name, description, required in zip(requirement_slugs, requirement_name_old, requirement_description_old, is_required_old):
                if slug and name:
                    job_requirement = JobRequirement.objects.get(slug=slug)
                    job_requirement.requirement_name = name
                    job_requirement.requirement_description = description
                    job_requirement.is_required = required
                    job_requirement.save()

            # Add new requirements
            print('requirement_name', requirement_name)
            print('requirement_description', requirement_description)
            print('is_required', is_required)
            for name, description, required in zip(requirement_name, requirement_description, is_required):
                print('name', name, description, required)

                job_requirement_object = JobRequirement(
                    classified_job=job_object,
                    requirement_name=name,
                    requirement_description=description,
                    is_required=required
                )
                job_requirement_object.save()


            messages.success(request, _("Job Update Successfully"), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('job:AdminJobList'))
        else:
            messages.error(request, _("Job Not Update , Please Try Again"), extra_tags='Job')

    context = {
        'job': job,
        'requirement': requirement,
        'job_form': AdminJobForm(),
        'requirement_form': AdminJobRequirementForm(),
        'current_page': _('Update Job'),
        'prev_Page': _('Jobs'),
        'prev_Page_link': reverse_lazy('job:AdminJobList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/job/job/update.html', context)


@authenticated_staff
@staff_only
def AdminJobDelete(request, slug):
    job = Job.objects.get(slug=slug)
    if request.method == "POST":
        job.delete()
        messages.success(request, _("Job Delete Successfully"), extra_tags='Job')
        return HttpResponseRedirect(reverse_lazy('job:AdminJobList'))
    

####### ------------------------- Requests End Points ------------------------- #######
def AdminJobRequestsList(request, progress):
    allowed_progress = ['New', 'In Progress', 'Completed', 'Canceled']
    if progress not in allowed_progress:
        return redirect('job:AdminJobRequestsList', progress='New')
    requests = JobRequest.objects.filter(Progress=progress).select_related('user', 'classified_job')

    return render(request, f'{BACKEND_TEMPLATES}/job/requests/requests_list.html', {
        'requests': requests,
        'current_page': _(f'{progress} Requests'),
        'progress': progress,
    })



