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
@job_provider_only
def ProviderCompanyEmployeeList(request):
    provider = JobProvider.objects.get(user=request.user)
    if provider.type != 'Company':
        messages.error(request, _("You must be a company provider to manage employees."), extra_tags='Employee')
        return HttpResponseRedirect(reverse_lazy('provider:AdminJobProviderList'))
    employees = JobProviderEmployee.objects.filter(provider__user=request.user)


    context = {
        'employees': employees,
        'employee_form': AdminJobProviderEmployeeForm(),
        'current_page': _('Employees'),
        'prev_Page': _('Provider'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/employee/admin.html', context)

@job_provider_only
def ProviderCompanyEmployeeCreate(request):
    provider = JobProvider.objects.get(user=request.user)
    if provider.type != 'Company':
        messages.error(request, _("You must be a company provider to manage employees."), extra_tags='Employee')
        return HttpResponseRedirect(reverse_lazy('provider:AdminJobProviderList'))
    employees = JobProviderEmployee.objects.filter(provider__user=request.user)
    if request.method == "POST":
        employee_form = AdminJobProviderEmployeeForm(request.POST or None, request.FILES or None)
        if employee_form:

            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            image = request.FILES.get('image')

            role = request.POST.get('role')

            #check user by email if empty create one  if exist returnn message error
            check_users = User.objects.filter(email=email)


            if check_users.exists() :
                messages.error(request, _("Email already exists, please use a different email."), extra_tags='ProviderEmployee')
                return HttpResponseRedirect(reverse_lazy('provider:ProviderCompanyEmployeeList'))
            check_users = User.objects.filter(phone=phone)

            if check_users.exists() :
                messages.error(request, _("Phone already exists, please use a different phone."), extra_tags='ProviderEmployee')
                return HttpResponseRedirect(reverse_lazy('provider:ProviderCompanyEmployeeList'))

            # Create a new user if the email does not exist
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                image = image,
                is_active='Active',
                access_level='ProviderEmployee',
            )
            user.save()
            password = RandomPasswordGenerator()
            user.set_password(password)
            user.save()

            employee_object = JobProviderEmployee(
                provider=provider,
                user=user,
                role = role,
            )
            employee_object.save()

            messages.success(request, _("Employee Add Successfully"), extra_tags='ProviderEmployee')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderCompanyEmployeeList'))
        else:
            messages.error(request, _("Employee Not Add , Please Try Again"), extra_tags='ProviderEmployee')

    context = {
        'employees': employees,
        'employee_form': AdminJobProviderEmployeeForm(),
        'current_page': _('Employees'),
        'prev_Page': _('Provider'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/employee/add.html', context)

@job_provider_only
def ProviderCompanyEmployeeUpdate(request, slug):
    employee = JobProviderEmployee.objects.get(slug=slug)
    if request.method == "POST":
        employee_form = AdminJobProviderEmployeeForm(request.POST or None, request.FILES or None)

        if employee_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            image = request.FILES.get('image')

            role = request.POST.get('role')

            employee_object = JobProviderEmployee.objects.get(id=employee.id)
            employee_object.user.first_name = first_name
            employee_object.user.middle_name = middle_name
            employee_object.user.last_name = last_name
            employee_object.user.email = email
            employee_object.user.phone = phone
            if image:
                employee_object.user.image = image
            else:
                employee_object.user.image = employee_object.user.image
            employee_object.role = role
            employee_object.user.save()
            employee_object.save()

            messages.success(request, _("Employee Update Successfully"), extra_tags='ProviderEmployee')
            return HttpResponseRedirect(reverse_lazy('provider:ProviderCompanyEmployeeList'))
        else:
            messages.error(request, _("Employee Not Update , Please Try Again"), extra_tags='ProviderEmployee')

    context = {
        'employee': employee,
        'employee_form': AdminJobProviderEmployeeForm(),
        'current_page': _('Update Employee'),
        'prev_Page': _('Employees'),
        'prev_Page_link': reverse_lazy('provider:ProviderCompanyEmployeeList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/job_provider/employee/update.html', context)


@job_provider_only
def ProviderCompanyEmployeeDelete(request, slug):
    employee = JobProviderEmployee.objects.get(slug=slug)
    if request.method == "POST":
        employee.delete()
        messages.success(request, _("Employee Delete Successfully"), extra_tags='ProviderEmployee')
        return HttpResponseRedirect(reverse_lazy('provider:ProviderEmployeeList'))



