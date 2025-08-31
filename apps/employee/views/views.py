from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.customer.models.models import Employee
from apps.employee.forms.forms import AdminEmployeeForm
from helper.commonHelper import *
from helper.decorators import *

# Assumption: Your models are in one of these locations. Adjust as needed.

User = get_user_model()


########################## Classified Category Admin ################################
# Note: These are the functions you provided as a reference.

@authenticated_staff
@staff_only
def AdminEmployeeList(request):
    employee = User.objects.filter(access_level='Employee').order_by('-id')
    if request.method == "POST":
        employee_form = AdminEmployeeForm(request.POST or None, request.FILES or None)
        if employee_form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            position = request.POST.get('position')
            department = request.POST.get('department')
            hire_date = request.POST.get('hire_date')
            password = request.POST.get('password')
            is_active = True if request.POST.get('is_active') == 'on' else False

            if User.objects.filter(email=email).exists():
                messages.error(request, _("Email already exists"), extra_tags='Employee')
                return HttpResponseRedirect(reverse_lazy('employee:AdminEmployeeList'))

            user_object = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
                access_level='Employee',
                is_active=is_active
            )
            user_object.save()
            employee_object = Employee(
                user=user_object,
                position=position,
                department=department,
                hire_date=hire_date
            )
            employee_object.save()
            messages.success(request, _("Employee Created Successfully"), extra_tags='Employee')
            return HttpResponseRedirect(reverse_lazy('employee:AdminEmployeeList'))
        else:
            messages.error(request, _("Employee Not Created, Please Try Again"), extra_tags='Employee')
    else:
        employee_form = AdminEmployeeForm()
    context = {
        'employee': employee,
        'employee_form': employee_form,
        'current_page': _('Employee')
    }
    return render(request, f'{BACKEND_TEMPLATES}/employee/employee/admin.html',context)



@authenticated_staff
@staff_only
def AdminEmployeeUpdate(request, slug):
    employee = Employee.objects.get(slug=slug)
    user = employee.user
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        position = request.POST.get('position')
        department = request.POST.get('department')
        hire_date = request.POST.get('hire_date')
        password = request.POST.get('password')
        is_active = True if request.POST.get('is_active') == 'on' else False

        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, _("Email already exists"), extra_tags='Employee')
            return HttpResponseRedirect(reverse_lazy('employee:AdminEmployeeList'))

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.is_active = is_active
        if password:
            user.set_password(password)
        user.save()

        employee.position = position
        employee.department = department
        employee.hire_date = hire_date
        employee.save()

        messages.success(request, _("Employee Updated Successfully"), extra_tags='Employee')
        return HttpResponseRedirect(reverse_lazy('employee:AdminEmployeeList'))

    context = {
        'employee': employee,
        'user': user,
        'current_page': _('Employee')
    }
    return render(request, f'{BACKEND_TEMPLATES}/employee/employee/edit.html', context)


@authenticated_staff
@staff_only
def AdminEmployeeDelete(request, slug):
    employee = get_object_or_404(Employee, slug=slug)
    user = employee.user
    employee.delete()
    user.delete()
    messages.success(request, _("Employee Deleted Successfully"), extra_tags='Employee')
    return HttpResponseRedirect(reverse_lazy('employee:AdminEmployeeList'))


