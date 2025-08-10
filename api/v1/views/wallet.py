from unittest import TestCase

from django.contrib.auth import get_user_model
from django.core import mail
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from api.v1.serializers.app.wallet import PaymentGatewaySerializer
from apps.wallet.models.Payment import PaymentGateway
from apps.wallet.models.models import WalletResetPassword, WalletLocked
from core.utils.utils import Util

User = get_user_model()


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def ApiJobsPaymentGatewayList(request):
    """
    API endpoint to handle job payment gateway requests.
    """
    if request.method == 'GET' or request.method == 'POST':
        try:
            payment_gateways = PaymentGateway.objects.filter(status='Active')

            # ▼▼▼ USE YOUR NEW SERIALIZER ▼▼▼
            serializer = PaymentGatewaySerializer(payment_gateways, many=True, context={'request': request})

            return Response({'gateway_list': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
