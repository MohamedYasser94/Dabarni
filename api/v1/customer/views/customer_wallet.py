# apps/wallet/views/wallet_views.py
from decimal import Decimal
import uuid

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.contenttypes.models import ContentType

from apps.wallet.models.models import Wallet, WalletMoney, WalletLocked
from apps.wallet.models.transaction import TreasuryTransactions
from api.v1.customer.serializers.wallet import (
    WalletSerializer,
    WalletMoneySerializer,
    CreateWalletSerializer,
    DepositSerializer,
    WithdrawSerializer,
    TreasuryTransactionSerializer,
)


def _get_user_nuc(user):
    return getattr(user, "username", None) or getattr(user, "email", None) or str(getattr(user, "id", ""))


@extend_schema(
    description="Create new wallet for authenticated user",
    request=CreateWalletSerializer,
    responses={201: WalletSerializer},
    tags=["Customer Wallet"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_wallet(request):
    user = request.user

    if Wallet.objects.filter(user=user).exists():
        return Response({"status": False, "message": "Wallet already exists"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CreateWalletSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    password = serializer.validated_data.get("password", "123456")
    user_nuc = serializer.validated_data.get("user_nuc") or _get_user_nuc(user)
    amount = serializer.validated_data.get("amount", Decimal("0.00"))

    wallet_code = f"WALLET-{uuid.uuid4().hex[:6].upper()}"

    with transaction.atomic():
        locked = WalletLocked.objects.create(
            user=user,
            user_nuc=user_nuc,
            wallet_code=wallet_code,  
            password=password
        )

        wallet = Wallet.objects.create(
            wallet_locked=locked,
            user=user,
            user_nuc=user_nuc,
            code=wallet_code,
            amount=amount
        )

        WalletMoney.objects.create(
            wallet=wallet,
            user=user,
            actual_balance=amount,
            receive=Decimal("0.00"),
            send=Decimal("0.00"),
            paid=Decimal("0.00")
        )

    return Response({
        "status": True,
        "message": "Wallet created successfully",
        "data": WalletSerializer(wallet).data
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    description="Deposit money into wallet",
    request=DepositSerializer,
    responses={200: WalletMoneySerializer},
    tags=["Customer Wallet"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_money(request):
    serializer = DepositSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data["amount"]
    user = request.user

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().filter(user=user).first()
        if not wallet:
            return Response({"status": False, "message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        wallet.amount = (wallet.amount or Decimal("0.00")) + amount
        wallet.save()

        wallet_money, created = WalletMoney.objects.select_for_update().get_or_create(
            wallet=wallet,
            user=user,
            defaults={
                "actual_balance": Decimal("0.00"),
                "receive": Decimal("0.00"),
                "send": Decimal("0.00"),
                "paid": Decimal("0.00"),
            }
        )

        wallet_money.actual_balance = (wallet_money.actual_balance or Decimal("0.00")) + amount
        wallet_money.receive = (wallet_money.receive or Decimal("0.00")) + amount
        wallet_money.save()

        # Create TreasuryTransactions record for tracking payment history
        user_content_type = ContentType.objects.get_for_model(user)
        from datetime import datetime
        now = datetime.now()

        treasury_transaction = TreasuryTransactions.objects.create(
            wallet=wallet,
            owner_model=user_content_type,
            owner_id=user.id,
            transaction_type='Deposit',
            transaction_mode='Wallet',
            transaction_status='Complete',
            transaction_category='Income',
            amount=amount,
            receive=amount,
            send=Decimal("0.00"),
            note=f"Deposit of {amount} to wallet",
            month=str(now.month),
            year=str(now.year),
            status=True
        )

    return Response({
        "status": True,
        "message": "Deposit successful",
        "data": WalletMoneySerializer(wallet_money).data
    }, status=status.HTTP_200_OK)


@extend_schema(
    description="Withdraw money from wallet",
    request=WithdrawSerializer,
    responses={200: WalletMoneySerializer},
    tags=["Customer Wallet"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_money(request):
    serializer = WithdrawSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    amount = serializer.validated_data["amount"]
    user = request.user

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().filter(user=user).first()
        if not wallet:
            return Response({"status": False, "message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        current_amount = wallet.amount or Decimal("0.00")
        if current_amount < amount:
            return Response({"status": False, "message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.amount = current_amount - amount
        wallet.save()

        wallet_money, created = WalletMoney.objects.select_for_update().get_or_create(
            wallet=wallet,
            user=user,
            defaults={
                "actual_balance": Decimal("0.00"),
                "receive": Decimal("0.00"),
                "send": Decimal("0.00"),
                "paid": Decimal("0.00"),
            }
        )

        wallet_money.actual_balance = (wallet_money.actual_balance or Decimal("0.00")) - amount
        wallet_money.paid = (wallet_money.paid or Decimal("0.00")) + amount
        wallet_money.save()

    return Response({
        "status": True,
        "message": "Withdrawal successful",
        "data": WalletMoneySerializer(wallet_money).data
    }, status=status.HTTP_200_OK)


@extend_schema(
    description="Get wallet balance",
    responses={200: WalletSerializer},
    tags=["Customer Wallet"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    user = request.user
    wallet = Wallet.objects.filter(user=user).first()
    if not wallet:
        return Response({"status": False, "message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "status": True,
        "message": "Balance fetched successfully",
        "data": WalletSerializer(wallet).data
    }, status=status.HTTP_200_OK)


@extend_schema(
    description="Get list of user payment transactions",
    responses={200: TreasuryTransactionSerializer(many=True)},
    tags=["Customer Wallet"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    """Get list of user payment transactions from TreasuryTransactions"""
    user = request.user
    user_content_type = ContentType.objects.get_for_model(user)

    # Get transactions where the user is the owner
    transactions = TreasuryTransactions.objects.filter(
        owner_model=user_content_type,
        owner_id=user.id
    ).order_by('-create_at')

    return Response({
        "status": True,
        "message": "Transactions fetched successfully",
        "data": TreasuryTransactionSerializer(transactions, many=True).data
    }, status=status.HTTP_200_OK)

