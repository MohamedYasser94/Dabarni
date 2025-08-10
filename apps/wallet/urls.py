from django.urls import path

from apps.wallet.views import purchase, payments
from apps.wallet.views.wallet import UserWalletLocked, CreateWallet, AdminWalletUserView, UserWalletChangeInfo, \
    walletLogout, AdminWalletUserReset

app_name = 'wallet'

urlpatterns = [

    # ########## Wallet Admin #########

     path('wallet/lock/', UserWalletLocked, name='AdminUserWalletLocked'),
    path('wallet/add/', CreateWallet, name='AdminCreateWallet'),
    path('wallet/user/<slug:slug>', AdminWalletUserView, name='AdminWalletUserView'),
    path('wallet/change/<slug:slug>', UserWalletChangeInfo, name='AdminWalletChangeInfo'),
    path('wallet/logout/<slug:slug>', walletLogout, name='AdminWalletUserLogout'),
    path('wallet/rerset/', AdminWalletUserReset, name='AdminWalletUserReset'),

    # ########## Wallet Bank Transaction Admin #########
    path('wallet/purchase/transaction/', purchase.AdminPurchaseTransaction, name='AdminPurchaseTransaction'),

    ############# PayMent ##################
    path('wallet/payment/gateway/', payments.AdminPaymentGatewayList, name='AdminPaymentGatewayList'),
    # path('payment/gateway/create/', payment.AdminPaymentGatewayCreate, name='AdminPaymentGatewayCreate'),
    path('wallet/payment/gateway/edit/<slug:slug>/', payments.AdminPaymentGatewayUpdate, name='AdminPaymentGatewayUpdate'),
    path('wallet/payment/gateway/delete/<slug:slug>/', payments.AdminPaymentGatewayDelete, name='AdminPaymentGatewayDelete'),

]
