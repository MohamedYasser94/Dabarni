from django.contrib import admin
from apps.wallet.models.models import (
    Wallet, WalletMoney, WalletLocked, WalletResetPassword, 
    SystemWallet, PendingBalanceTransfer
)


@admin.register(WalletMoney)
class WalletMoneyAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'actual_balance', 'reversed_balance', 'status', 'update_at']
    list_filter = ['status']
    search_fields = ['user__email', 'user__phone', 'code']
    readonly_fields = ['code', 'slug', 'create_at', 'update_at']


@admin.register(PendingBalanceTransfer)
class PendingBalanceTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'created_at', 'transfer_at', 'transferred_at']
    list_filter = ['status', 'created_at', 'transfer_at']
    search_fields = ['user__email', 'user__phone']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transfer Info', {'fields': ('wallet_money', 'user', 'amount', 'status')}),
        ('Job Reference', {'fields': ('job_content_type', 'job_id')}),
        ('Timing', {'fields': ('created_at', 'transfer_at', 'transferred_at')}),
        ('Notes', {'fields': ('notes',)}),)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'create_at']
    list_filter = ['status']
    search_fields = ['user__email', 'code']

@admin.register(WalletLocked)
class WalletLockedAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'create_at']
    list_filter = ['status']

@admin.register(SystemWallet)
class SystemWalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'earning', 'profit', 'create_at']