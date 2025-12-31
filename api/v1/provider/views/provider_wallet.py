from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from api.v1.provider.serializers.classified import *
from api.v1.provider.serializers.wallet import PayoutRequestSerializer, ProviderWalletMoneySerializer, PaymentGatewaySerializer, \
    BankAccountSerializer
from apps.classified.models.models import *
from apps.wallet.models.payment import PaymentGateway, BankAccount
from apps.wallet.models.models import WalletMoney
from apps.wallet.models.transaction import PayoutRequest
from django.db import transaction

@extend_schema(
    tags=["Provider Wallet"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderWallet(request):
    try:
        wallet, created = WalletMoney.objects.get_or_create(user=request.user)
        serializer = ProviderWalletMoneySerializer(wallet)
        message = "Wallet created successfully" if created else "Wallet fetched successfully"

        return Response({
            "status": True,
            "message": message,
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "status": False,
            "message": f"An error occurred: {str(e)}",
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Provider Wallet"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderPayoutRequest(request):
    try:
        provider = JobProvider.objects.get(user=request.user)
    except JobProvider.DoesNotExist:
        return Response({
            "status": False,
            "message": "Provider profile not found for this user",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PayoutRequestSerializer(data=request.data)
    if serializer.is_valid():
        try:
            amount = Decimal(str(serializer.validated_data.get("amount")))
        except:
            return Response({
                "status": False,
                "message": "Invalid amount format",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if amount <= 0:
            return Response({
                "status": False,
                "message": "Amount must be greater than 0",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                wallet = WalletMoney.objects.select_for_update().filter(user=request.user).first()

                if not wallet:
                    return Response({
                        "status": False,
                        "message": "Wallet not found",
                        "data": {}
                    }, status=status.HTTP_404_NOT_FOUND)

                if wallet.actual_balance < amount:
                    return Response({
                        "status": False,
                        "message": "Insufficient balance",
                        "data": {}
                    }, status=status.HTTP_400_BAD_REQUEST)

                wallet.actual_balance -= amount
                wallet.save()
                payout_request = serializer.save(user=request.user, status="PENDING")

                return Response({
                    "status": True,
                    "message": "Payout request created successfully",
                    "data": PayoutRequestSerializer(payout_request).data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": False,
                "message": f"Transaction failed: {str(e)}",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": False,
        "message": "Validation error",
        "data": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Provider Wallet"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderPayoutRequestList(request):
    try:
        provider = JobProvider.objects.get(user=request.user)
    except JobProvider.DoesNotExist:
        return Response({
            "status": False,
            "message": "Provider profile not found",
            "data": []
        }, status=status.HTTP_404_NOT_FOUND)

    payout_requests = PayoutRequest.objects.filter(user=request.user).order_by('-created_at')
    serializer = PayoutRequestSerializer(payout_requests, many=True)

    return Response({
        "status": True,
        "message": "Payout requests fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderPayoutRequestDetail(request, payout_id):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        payout = PayoutRequest.objects.get(id=payout_id, provider=provider)
    except PayoutRequest.DoesNotExist:
        return Response({
            "status": False,
            "message": "Payout request not found",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = PayoutRequestSerializer(payout)
    return Response({
        "status": True,
        "message": "Payout request details fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderPayoutRequestDetail(request, payout_id):
    provider = JobProvider.objects.get(id=request.user.id)
    try:
        payout = PayoutRequest.objects.get(id=payout_id, provider=provider)
    except PayoutRequest.DoesNotExist:
        return Response({
            "status": False,
            "message": "Payout request not found",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    payout_data = {
        "id": payout.id,
        "amount": payout.amount,
        "status": payout.status,
        "requested_at": payout.created_at,
        "processed_at": payout.processed_at
    }

    return Response({
        "status": True,
        "message": "Payout request details fetched successfully",
        "data": payout_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def PaymentGatewayList(request):
    gateways = PaymentGateway.objects.all()
    serializer = PaymentGatewaySerializer(gateways, many=True)

    return Response({
        "status": True,
        "message": "Payment gateways fetched successfully",
        "data": serializer.data
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderBankAccount(request):
    provider = JobProvider.objects.get(user=request.user)
    bank_account = BankAccount.objects.filter(user=request.user).first()

    if bank_account:
        bank_account_serializer = BankAccountSerializer(bank_account)
        return Response({
            "status": True,
            "message": "Bank account fetched successfully",
            "data": bank_account_serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "status": False,
            "message": "Bank account not found",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    description="Add new provider bank account",
    request=BankAccountSerializer,
    responses={201: BankAccountSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddProviderBankAccount(request):
    try:
         provider, _ = JobProvider.objects.get_or_create(user=request.user)  # ✅ تعديل 
    except JobProvider.DoesNotExist:
        return Response({
            "status": False,
            "message": "Provider profile not found",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = BankAccountSerializer(data=request.data)
    if serializer.is_valid():
        default_account = serializer.validated_data.get("default_account", False)

        if default_account:
            BankAccount.objects.filter(user=request.user, default_account=True).update(default_account=False)

        bank_account = serializer.save(user=request.user)

        return Response({
            "status": True,
            "message": "Bank account added successfully",
            "data": BankAccountSerializer(bank_account).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        "status": False,
        "message": "Validation error",
        "data": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
