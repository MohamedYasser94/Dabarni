from django.contrib import messages
from django.shortcuts import render , redirect
from django.utils import timezone


from apps.classified.models.job import *
from apps.wallet.models.billing import Purchase
from helper.commonHelper import ACTIVE_FRONTEND_TEMPLATES


def FrontProviderList(request):
    providers = JobProvider.objects.filter(status='Active').order_by('-id')
    context = {
        'providers': providers,
    }

    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/contact/termsofservice.html',context )


def FrontProviderJobAdd(request):
    # This view is for adding a job by the provider
    # You can implement the logic for adding a job here

    if request.method == 'POST':
        # Handle the form submission for adding a job
        # You can use a form class to validate and save the job data
        job_form  = AdminJobForm(request.POST, request.FILES)
        if job_form:
            user = request.user
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

            # Create a new job instance
            job_object = Job(
                user=user,
                title=title,
                description=description,
                category_id=category,
                location_id=location,
                cost=cost,
                cost_type=cost_type,
                duration=duration,
                need_requirements=need_requirements,
                image=image,
                is_featured=is_featured,
                negotiable=negotiable
            )
            job_object.save()

            # Create job requirements
            for i in range(len(requirement_type)):
                requirement = JobRequirement(
                    classified_job=job_object,
                    requirement_type=requirement_type[i],
                    requirement_name=requirement_name[i],
                    requirement_description=requirement_description[i],
                    is_required=is_required[i]
                )
                requirement.save()
            # Redirect to a success page or render a success message
            messages.success(request, 'Job Posted Successfully',extra_tags='FrontProviderJobAdd')
            return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/post_job_success.html', {'job': job_object})
        else:
            messages.error(request, 'Failed to post job. Please check the form data.', extra_tags='FrontProviderJobAdd')
    else:
        # Render the job posting form
        job_form = AdminJobForm()
    context = {
        'job_form': job_form,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/post_job.html',context )

def FrontProviderCategoryList(request):
    category = JobCategories.objects.filter(parent=None,status='Active').order_by('title')
    context = {
        'category': category,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/category_list.html', context)

def FrontProviderCategoryDetail(request, slug):
    try:
        category = JobCategories.objects.get(slug=slug, status='Active')
    except JobCategories.DoesNotExist:
        category = None
    if category is None:
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/404.html', status=404)
    jobs = Job.objects.filter(category=category,status='Active').order_by('-id')
    context = {
        'category': category,
        'jobs': jobs,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/category_detail.html', context)






def FrontProviderJobList(request):
    jobs = Job.objects.filter(status='Active').order_by('-id')
    context = {
        'jobs': jobs,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/job_list.html',context )

def FrontProviderJobDetail(request, slug):
    try:
        job = Job.objects.select_related('provider', 'category', 'location').get(slug=slug, status='Active')
        provider = JobProvider.objects.get(id=job.provider.id)
        job_user = User.objects.get(id=provider.user.id)

    except Job.DoesNotExist:
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/404.html', status=404)

    job_requirements = JobRequirement.objects.filter(classified_job=job)

    user_request = None
    if request.user.is_authenticated:
        user_request = JobRequest.objects.filter(classified_job=job, user=request.user).first()

    proposal_form = JobRequestForm()

    job.views += 1
    job.save()
    context = {
        'job': job,
        'job_user': job_user,
        'job_requirements': job_requirements,
        'user_request': user_request,     
        'proposal_form': proposal_form,  
    }
    
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/job_detail.html', context)


def FrontSubmitJobRequest(request, slug):
    try:
        job = Job.objects.get(slug=slug, status='Active')
        provider = JobProvider.objects.get(id=job.provider.id)
        job_user = User.objects.get(id=provider.user.id)
    except Job.DoesNotExist:
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/404.html', status=404)


    job_requirements = JobRequirement.objects.filter(classified_job=job)

    if request.method == 'POST':
   
        if not JobRequest.objects.filter(classified_job=job, user=request.user).exists():
            message = request.POST.get('message', '')
            attachment = request.FILES.get('attachment', None)

            JobRequest.objects.create(
                classified_job=job,
                user=request.user,
                message=message,
                attachment=attachment,
                price=job.cost,
                final_price=job.cost,
                progress="New"
            )
            messages.success(request, 'Your request has been submitted successfully!')
        else:
            messages.error(request, 'You have already submitted a request for this job.')

    
    user_request = JobRequest.objects.filter(classified_job=job, user=request.user).first()
  
    proposal_form = JobRequestForm()
    

    context = {
        'job': job,
        'job_user': job_user,
        'user_request': user_request,
        'proposal_form': proposal_form,
        'job_requirements': job_requirements, 
    }
    

    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/job_detail.html', context)


def FrontProviderJobPayment(request, slug):
    try:
        job_request = JobRequest.objects.get(slug=slug,)
    except JobRequest.DoesNotExist:
        messages.error(request, 'The job request does not exist or you do not have permission to access it.')
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/404.html', status=404)
    user = request.user
    purchase = Purchase(
        sender_model=ContentType.objects.get(model='JobRequest'),
        sender_id=job_request.id,
        receiver_model=ContentType.objects.get(model='JobProvider'),
        receiver_id=job_request.classified_job.provider.id,
        owner_model=ContentType.objects.get(model='User'),
        owner_id=user.id,
        amount=job_request.final_price,
        source='Web',
        purchase_date=timezone.now(),
    )
    purchase.save()
    messages.success(request, 'Payment processed successfully!')
    return redirect('home:PaymentPayTabs', slug=purchase.slug)

def payment_success(request):
    """
    This view handles the successful payment response.
    It can be used to display a success message or redirect to a specific page.
    """
    messages.success(request, 'Payment was successful!')
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/payment/success.html')

def Upload_job_requirements(request, slug):
    try:
       
        user_request = JobRequest.objects.get(slug=slug, user=request.user)
    except JobRequest.DoesNotExist:
        messages.error(request, 'the request does not exist or you do not have permission to access it.')
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/404.html', status=404)

   
    job_requirements = JobRequirement.objects.filter(classified_job=user_request.classified_job)

    if request.method == 'POST':
        for requirement in job_requirements:
            
            file_key = f'requirement_{requirement.id}'
            uploaded_file = request.FILES.get(file_key)
            
            if uploaded_file:
             
                JobRequestDocument.objects.update_or_create(
                    job_request=user_request,
                    job_requirement=requirement,
                    defaults={'document': uploaded_file}
                )
        
        messages.success(request, 'Documents uploaded successfully!')
        print("User request done :", user_request)
        return redirect('home:job_detail', slug=user_request.classified_job.slug)
    return redirect('home:job_detail', slug=user_request.classified_job.slug)


def CheckProvider(request):
    if not request.user.is_authenticated:
        return redirect('home:FrontJobList')

    try:
        provider = JobProvider.objects.get(user=request.user, status='Active')
    except:
        try:
            employee = JobProviderEmployee.objects.get(user=request.user, status='Active')
            provider = JobProvider.objects.get(id=employee.provider.id, status='Active')
        except:
            return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/error/404.html', status=404)

    return provider

#################### Job provider Dashboard ####################
def FrontProviderDashboard(request):
    if not request.user.is_authenticated:
        return redirect('home:FrontJobList')


    provider = CheckProvider(request)
    try:

        jobs = Job.objects.filter(provider=provider, status='Active').order_by('-id')
        job_requests = JobRequest.objects.filter( classified_job__provider=provider, status='Active').order_by('-id')
    except:
        jobs = []
        job_requests = []

    context = {
        'jobs': jobs,
        'job_requests': job_requests,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/dashboard.html', context)

def FrontProviderJobRequestList(request):
    if not request.user.is_authenticated:
        return redirect('home:FrontJobList')

    provider = CheckProvider(request)

    job_requests = JobRequest.objects.filter(classified_job__provider__id=provider.id, status='Active').order_by('-id')

    context = {
        'job_requests': job_requests,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/job_list.html', context)

def FrontProviderJobEdit(request, slug):
    try:
        job_request = JobRequest.objects.get(slug=slug, user=request.user, status='Active')
    except JobRequest.DoesNotExist:
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/404.html', status=404)

    if request.method == 'POST':
        form = JobRequestForm(request.POST, instance=job_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job request updated successfully!')
            return redirect('home:FrontProviderJobRequestList')
        else:
            messages.error(request, 'Failed to update job request. Please check the form data.')
    else:
        form = JobRequestForm(instance=job_request)

    context = {
        'form': form,
        'job_request': job_request,
    }
    return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/edit-job.html', context)

def FrontProviderJobChat(request, dialog_id=None):
    """
    provider chat view - redirects to the main chat room view
    """
    if not request.user.is_authenticated:
        return redirect('home:FrontJobList')
    
    # Check if provider is authorized
    provider = CheckProvider(request)
    
    if dialog_id:
        # Redirect to the main chat room view
        return redirect('home:FrontChatRoom', dialog_id=dialog_id)
    else:
        # Show chat list page or redirect to dialog selection
        from core.models.chat import Dialog
        from django.db.models import Q
        
        # Get all dialogs for this provider
        dialogs = Dialog.objects.filter(
            Q(provider=request.user) | Q(customer=request.user)
        ).select_related('provider', 'customer').prefetch_related('messages')
        
        context = {
            'dialogs': dialogs,
        }
        return render(request, f'{ACTIVE_FRONTEND_TEMPLATES}/provider/dashboard/chat_list.html', context)
