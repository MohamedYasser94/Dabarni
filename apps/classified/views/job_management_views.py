# D:\Python Projects\Dabarni_fork\Dabarni\apps\employee\views\job_management_views.py

from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Prefetch, Count
from django.utils.translation import gettext_lazy as _
from helper.commonHelper import *
from helper.decorators import *
from helper.decorators import authenticated_staff, staff_only
from apps.classified.models.models import Job, JobOffer, JobNegotiate, JobProgress, JobProvider


def authenticated_staff(view_func):
    return view_func

def staff_only(view_func):
    return view_func

# --- قائمة الطلبات (All Jobs) ---
@authenticated_staff
@staff_only
def AdminJobList(request):
    jobs = (
        Job.objects
        .select_related('customer', 'category')
        .prefetch_related(
            Prefetch('progresses', queryset=JobProgress.objects.all().order_by('-create_at')),
            Prefetch('offers', queryset=JobOffer.objects.select_related('provider__user'))
        )
        .annotate(
            offers_count=Count('offers')
        )
        .all()
    )
    context = {
        'jobs': jobs,
        'current_page': _('All Jobs')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/job/jobs_list.html', context)


# --- الطلبات النشطة (Active Jobs) ---
@authenticated_staff
@staff_only
def AdminActiveJobs(request):
    jobs = (
        Job.objects
        .filter(progresses__progress_status__in=['Negotiation', 'In Progress'])
        .select_related('customer', 'category')
        .prefetch_related(
            Prefetch('progresses', queryset=JobProgress.objects.select_related('provider').all().order_by('-create_at')),
            Prefetch('offers', queryset=JobOffer.objects.select_related('provider__user'))
        )
        .annotate(
            offers_count=Count('offers')
        )
        .all()
    )
    context = {
        'jobs': jobs,
        'current_page': _('Active Jobs')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/job/jobs_list.html', context)


# --- الطلبات المكتملة (Completed Jobs) ---
@authenticated_staff
@staff_only
def AdminCompletedJobs(request):
    jobs = (
        Job.objects
        .filter(progresses__progress_status='Completed')
        .select_related('customer', 'category')
        .prefetch_related(
            Prefetch('progresses', queryset=JobProgress.objects.select_related('provider').all().order_by('-create_at')),
            Prefetch('offers', queryset=JobOffer.objects.select_related('provider__user'))
        )
        .annotate(
            offers_count=Count('offers')
        )
        .all()
    )
    context = {
        'jobs': jobs,
        'current_page': _('Completed Jobs')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/job/jobs_list.html', context)


# --- الطلبات الملغاة (Canceled Jobs) ---
@authenticated_staff
@staff_only
def AdminCanceledJobs(request):
    jobs = (
        Job.objects
        .filter(progresses__progress_status='Cancelled')
        .select_related('customer', 'category')
        .prefetch_related(
            Prefetch('progresses', queryset=JobProgress.objects.select_related('provider').all().order_by('-create_at')),
            Prefetch('offers', queryset=JobOffer.objects.select_related('provider__user'))
        )
        .annotate(
            offers_count=Count('offers')
        )
        .all()
    )
    context = {
        'jobs': jobs,
        'current_page': _('Canceled Jobs')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/job/jobs_list.html', context)


# --- إدارة العروض (Manage Offers) ---
@authenticated_staff
@staff_only
def AdminManageOffers(request):
    offers = (
        JobOffer.objects
        .select_related('job__customer', 'job__category', 'provider__user')
        .all()
        .order_by('-create_at')
    )
    context = {
        'offers': offers,
        'current_page': _('Manage Offers')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/job/offers_list.html', context)


# --- إدارة المفاوضات (Manage Negotiations) ---
@authenticated_staff
@staff_only
def AdminManageNegotiations(request):
    negotiations = (
        JobNegotiate.objects
        .select_related('job__customer', 'job__category', 'offer', 'provider__user', 'customer')
        .all()
        .order_by('-create_at')
    )
    context = {
        'negotiations': negotiations,
        'current_page': _('Manage Negotiations')
    }
    return render(request, f'{BACKEND_TEMPLATES}/classified/job/negotiations_list.html', context)