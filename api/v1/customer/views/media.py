
from django.utils import timezone
from httpcore import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from api.v1.constants import JobOfferStatus, JobProgressStatus
from apps.classified.models.models import Job, JobMedia, JobMedia, JobNegotiate, JobOffer, JobProgress
from django.db import transaction
from api.v1.customer.serializers.jop_request_serializer import (
    JobCreateSerializer,
    JobDetailSerializer,
    JobNegotiateCreateSerializer,
    ProviderOfferSerializer,
)
from api.v1.response import success_response, error_response
from apps.wallet.models.models import Wallet

@extend_schema(
    tags=["Jobs"],
    responses={200: JobDetailSerializer, 404: 'Not Found Response'}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    serializer = JobDetailSerializer(job, context={"request": request})
    return Response(serializer.data, status=200)
