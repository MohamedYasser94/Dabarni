from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.v1.provider.serializers.classified import *
from api.v1.provider.serializers.wallet import ProviderWalletMoneySerializer, PaymentGatewaySerializer, \
    BankAccountSerializer
from apps.classified.models.models import *
from apps.wallet.models.Payment import PaymentGateway, BankAccount
from apps.wallet.models.models import WalletMoney
from apps.wallet.models.transaction import PayoutRequest


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderWallet(request):
    provider = JobProvider.objects.get(id=request.user.id)
    wallet = WalletMoney.objects.filter(user=request.user).first()

    if wallet:
        wallet_serializer = ProviderWalletMoneySerializer(wallet)
        return Response({
            "status": True,
            "message": "Wallet fetched successfully",
            "data": wallet_serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "status": False,
            "message": "Wallet not found",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ProviderPayoutRequest(request):
    provider = JobProvider.objects.get(id=request.user.id)
    amount = request.data.get('amount')

    wallet = WalletMoney.objects.filter(user=request.user).first()

    if not wallet or wallet.actual_balance < float(amount):
        return Response({
            "status": False,
            "message": "Insufficient balance",
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

    # Deduct the amount from the wallet
    wallet.actual_balance -= float(amount)

    wallet.save()

    # Create a payout request
    payout_request = PayoutRequest.objects.create(
        provider=provider,
        amount=amount,
        status='PENDING'
    )

    return Response({
        "status": True,
        "message": "Payout request created successfully",
        "data": {
            "payout_request_id": payout_request.id,
            "amount": payout_request.amount,
            "status": payout_request.status
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderPayoutRequestList(request):
    provider = JobProvider.objects.get(id=request.user.id)
    payout_requests = PayoutRequest.objects.filter(provider=provider).order_by('-created_at')

    payout_data = []
    for payout in payout_requests:
        payout_data.append({
            "id": payout.id,
            "amount": payout.amount,
            "status": payout.status,
            "requested_at": payout.created_at,
            "processed_at": payout.processed_at
        })

    return Response({
        "status": True,
        "message": "Payout requests fetched successfully",
        "data": payout_data
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

    gateway_serializer = PaymentGatewaySerializer(gateways, many=True)
    return Response({
        "status": True,
        "message": "Payment gateways fetched successfully",
        "data": gateway_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ProviderBankAccount(request):
    provider = JobProvider.objects.get(id=request.user.id)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddProviderBankAccount(request):
    provider = JobProvider.objects.get(id=request.user.id)

    bank_name = request.data.get('bank_name')
    account_number = request.data.get('account_number')
    iban = request.data.get('iban')
    swift_code = request.data.get('swift_code')
    default_account = request.data.get('default_account', False)

    if default_account:
        # If setting this account as default, unset previous default accounts
        BankAccount.objects.filter(user=request.user, default_account=True).update(default_account=False)

    bank_account = BankAccount.objects.create(
        user=request.user,
        bank_name=bank_name,
        account_number=account_number,
        iban=iban,
        swift_code=swift_code,
        default_account=default_account
    )
    bank_account_serializer = BankAccountSerializer(bank_account,many=False)
    return Response({
        "status": True,
        "message": "Bank account added successfully",
        "data": bank_account_serializer.data
    }, status=status.HTTP_201_CREATED)






