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


##########  JobProvider Dashboard #########
@job_provider_only
def ProviderDashboard(request):
    try:
        provider = JobProvider.objects.get(user=request.user)
    except JobProvider.DoesNotExist:
        try:
            employee = JobProviderEmployee.objects.get(user=request.user)
            provider = JobProvider.objects.get(user=employee.provider.user)
        except JobProviderEmployee.DoesNotExist:
            provider = None
            messages.error(request, _("You must be a provider to view the dashboard."), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderDashboard'))

    context = {
        'provider': provider,
        'current_page': _('Dashboard'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/dashboard.html', context)

##########  Job  Admin #########

@job_provider_only
def ProviderJobList(request):
    try:
        provider = JobProvider.objects.get(user=request.user)
    except JobProvider.DoesNotExist:
        try:
            employee = JobProviderEmployee.objects.get(user=request.user)
            provider = JobProvider.objects.get(user=employee.provider.user)
        except JobProviderEmployee.DoesNotExist:
            provider = None
            messages.error(request, _("You must be a provider to view jobs."), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderJobList'))
    jobs = Job.objects.filter(provider=provider).select_related(
        'category',
        'location',
    ).order_by('-id')
    context = {
        'jobs': jobs,
        'current_page': _('Jobs')
    }
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/job/admin.html', context)


@job_provider_only
def ProviderJobCreate(request):
    try:
        provider = JobProvider.objects.get(user=request.user)
    except JobProvider.DoesNotExist:
        try:
            employee = JobProviderEmployee.objects.get(user=request.user)
            provider = JobProvider.objects.get(user=employee.provider.user)
        except JobProviderEmployee.DoesNotExist:
            provider = None
            messages.error(request, _("You must be a provider to view jobs."), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderJobList'))
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
            requirement_type = request.POST.getlist('[requirement_type]')
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
                provider = None
                messages.error(request, _("You must be a provider to add a job."), extra_tags='Job')
                return HttpResponseRedirect(reverse_lazy('provider:ProviderJobList'))

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

            for type , name, description, required in zip(requirement_type, requirement_name, requirement_description, is_required):
                if type and name:
                    job_requirement = JobRequirement(
                        classified_job=job_object,
                        requirement_type=type,
                        requirement_name=name,
                        requirement_description=description,
                        is_required=required
                    )
                    job_requirement.save()
            messages.success(request, _("Job Add Successfully"), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderJobList'))
        else:
            print('Job Form Error:', job_form.errors)
            messages.error(request, _("Job Not Add , Please Try Again"), extra_tags='Job')
    else:
        job_form = AdminJobForm()
        requirement_form = AdminJobRequirementForm()

    context = {
        'job_form': job_form,
        'requirement_form': requirement_form,
        'current_page': _('Add Job'),
        'prev_Page': _('Jobs'),
        'prev_Page_link': reverse_lazy('provider:ProviderJobList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/job/add.html', context)


@job_provider_only
def ProviderJobUpdate(request, slug):
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

            requirement_type = request.POST.getlist('[requirement_type]')
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
            for type, name, description, required in zip(requirement_type, requirement_name, requirement_description, is_required):
                if type and name:
                    job_requirement = JobRequirement(
                        classified_job=job_object,
                        requirement_type=type,
                        requirement_name=name,
                        requirement_description=description,
                        is_required=required
                    )
                    job_requirement.save()

            messages.success(request, _("Job Update Successfully"), extra_tags='Job')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderJobList'))
        else:
            messages.error(request, _("Job Not Update , Please Try Again"), extra_tags='Job')

    context = {
        'job': job,
        'requirement': requirement,
        'job_form': AdminJobForm(),
        'requirement_form': AdminJobRequirementForm(),
        'current_page': _('Update Job'),
        'prev_Page': _('Jobs'),
        'prev_Page_link': reverse_lazy('provider:ProviderJobList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/job_provider/job/update.html', context)


@job_provider_only
def ProviderJobDelete(request, slug):
    job = Job.objects.get(slug=slug)
    if request.method == "POST":
        job.delete()
        messages.success(request, _("Job Delete Successfully"), extra_tags='Job')
        return HttpResponseRedirect(reverse_lazy('provider:ProviderJobList'))
    

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





##################### Job Provider Error Pages #####################

def ProviderError404(request):
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/error/404.html', {
        'current_page': _('Error 404'),
    })