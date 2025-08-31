from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.provider.serializers.classified import *
from apps.classified.models.models import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderHome(request):
    provider = JobProvider.objects.get(id=request.user.id)
    job_progress = JobProgress.objects.filter(provider=provider)
    job_offer = JobOffer.objects.filter(provider=provider)

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, many=True,context={'request': request})
    job_offer_serializer = JobOfferSerializer(job_offer, many=True,context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderMyOrders(request,progress_status):
    provider = JobProvider.objects.get(id=request.user.id)
    job_progress = JobProgress.objects.filter(provider=provider,status=progress_status)
    job_offer = JobOffer.objects.filter(provider=provider,status=progress_status)

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, many=True,context={'request': request})
    job_offer_serializer = JobOfferSerializer(job_offer, many=True,context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobDetails(request,job_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job = Job.objects.get(slug=job_slug,provider=provider)
    except Job.DoesNotExist:
        return Response({"error": "Job not found or you do not have permission to view this job."}, status=status.HTTP_404_NOT_FOUND)

    ### serializers
    job_serializer = JobSerializer(job, context={'request': request})

    data = {
        "job": job_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobOfferDetails(request,offer_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_offer = JobOffer.objects.get(slug=offer_slug,provider=provider)
    except JobOffer.DoesNotExist:
        return Response({"error": "Job offer not found or you do not have permission to view this job offer."}, status=status.HTTP_404_NOT_FOUND)

    ### serializers
    job_offer_serializer = JobOfferSerializer(job_offer, context={'request': request})

    data = {
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobNegotiations(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to view this job progress."}, status=status.HTTP_404_NOT_FOUND)

    negotiations = JobNegotiate.objects.filter(job=job_progress.job,provider=provider)

    ### serializers
    negotiations_serializer = JobNegotiateSerializer(negotiations, many=True,context={'request': request})

    data = {
        "negotiations": negotiations_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateJobNegotiationStatus(request,negotiation_id):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_negotiation = JobNegotiate.objects.get(id=negotiation_id,provider=provider)
    except JobNegotiate.DoesNotExist:
        return Response({"error": "Job negotiation not found or you do not have permission to update this job negotiation."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'accepted', 'rejected']:
        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    job_negotiation.status = new_status
    job_negotiation.save()

    ### serializers
    job_negotiation_serializer = JobNegotiateSerializer(job_negotiation, context={'request': request})

    data = {
        "job_negotiation": job_negotiation_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobProgressDetails(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to view this job progress."}, status=status.HTTP_404_NOT_FOUND)

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateJobOfferStatus(request,offer_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_offer = JobOffer.objects.get(slug=offer_slug,provider=provider)
    except JobOffer.DoesNotExist:
        return Response({"error": "Job offer not found or you do not have permission to update this job offer."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'accepted', 'rejected', 'cancelled']:
        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    job_offer.status = new_status
    job_offer.save()

    ### serializers
    job_offer_serializer = JobOfferSerializer(job_offer, context={'request': request})

    data = {
        "job_offer": job_offer_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateJobProgressStatus(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    job_progress.status = new_status
    job_progress.save()

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jobRequestExtraMoney(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    extra_amount = request.data.get('extra_amount')
    reason = request.data.get('reason','')

    if not extra_amount or float(extra_amount) <= 0:
        return Response({"error": "Invalid extra amount."}, status=status.HTTP_400_BAD_REQUEST)

    job_negotiation = JobNegotiate.objects.create(
        job=job_progress.job,
        provider=provider,
        amount=extra_amount,
        reason=reason,
        status='pending'
    )

    ### serializers
    job_negotiation_serializer = JobNegotiateSerializer(job_negotiation, context={'request': request})

    data = {
        "job_negotiation": job_negotiation_serializer.data,
    }
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderJobCancelRequest(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    if job_progress.status == 'cancelled':
        return Response({"error": "Job progress is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

    job_progress.status = 'cancelled'
    job_progress.save()

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderJobCompleteRequest(request,progress_slug):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        job_progress = JobProgress.objects.get(slug=progress_slug,provider=provider)
    except JobProgress.DoesNotExist:
        return Response({"error": "Job progress not found or you do not have permission to update this job progress."}, status=status.HTTP_404_NOT_FOUND)

    if job_progress.status == 'completed':
        return Response({"error": "Job progress is already completed."}, status=status.HTTP_400_BAD_REQUEST)

    job_progress.status = 'completed'
    job_progress.save()

    ### serializers
    job_progress_serializer = JobProgressSerializer(job_progress, context={'request': request})

    data = {
        "job_progress": job_progress_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderProfile(request):
    provider = JobProvider.objects.get(id=request.user.id)

    ### serializers
    provider_serializer = JobProviderSerializer(provider, context={'request': request})

    data = {
        "provider": provider_serializer.data,
        "profile_completion_percentage": provider.profile_completion_percentage
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderUpdateProfile(request):
    try:
        # Get all related objects for the authenticated user
        user = request.user
        provider = user.job_provider_profile
        profile = user.profile
    except JobProvider.DoesNotExist:
        return Response({"error": "Provider profile not found."}, status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    # --- 1. Update User Model Fields ---
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.save()

    # --- 2. Update UserProfile Model Fields ---
    profile.dob = data.get('dob', profile.dob)
    profile.nationality = data.get('nationality', profile.nationality)
    profile.residence = data.get('residence', profile.residence)
    profile.id_number = data.get('id_number', profile.id_number)
    if 'id_image_front' in request.FILES:
        profile.id_image_front = request.FILES['id_image_front']
    if 'id_image_back' in request.FILES:
        profile.id_image_back = request.FILES['id_image_back']
    if 'residence_image' in request.FILES:
        profile.residence_image = request.FILES['residence_image']
    profile.save()

    # --- 3. Update JobProvider Model Fields ---
    provider.experience_years = data.get('experience_years', provider.experience_years)
    provider.company = data.get('company', provider.company)
    provider.bio = data.get('bio', provider.bio)
    provider.website = data.get('website', provider.website)
    provider.business_phone = data.get('business_phone', provider.business_phone)
    provider.address = data.get('address', provider.address)
    provider.commercial_number = data.get('commercial_number', provider.commercial_number)
    provider.vat_number = data.get('vat_number', provider.vat_number)
    provider.license_number = data.get('license_number', provider.license_number)
    provider.bank_account = data.get('bank_account', provider.bank_account)
    if 'commercial_image' in request.FILES:
        provider.commercial_image = request.FILES['commercial_image']
    if 'commercial_image2' in request.FILES:
        provider.commercial_image2 = request.FILES['commercial_image2']
    if 'vat_image' in request.FILES:
        provider.vat_image = request.FILES['vat_image']
    if 'license_image' in request.FILES:
        provider.license_image = request.FILES['license_image']

    # The save method will automatically recalculate the completion percentage
    provider.save()

    # Serialize the updated provider data
    provider_serializer = JobProviderSerializer(provider, context={'request': request})

    # Prepare the final response
    response_data = {
        "provider": provider_serializer.data,
        "profile_completion_percentage": provider.data_progress  # Use the saved field
    }

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderJobReviews(request):
    provider = JobProvider.objects.get(id=request.user.id)
    job_reviews = JobReview.objects.filter(provider=provider)

    ### serializers
    job_reviews_serializer = JobReviewSerializer(job_reviews, many=True,context={'request': request})

    data = {
        "job_reviews": job_reviews_serializer.data,
    }
    return Response(data, status=status.HTTP_200_OK)