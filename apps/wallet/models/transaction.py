from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.wallet.models.models import Wallet, SystemWallet
from helper.modelHelper import Transaction_Money_Type, Transaction_Money_Status, Transaction_Money_Category, \
    Transaction_Money_Mode,  Active_Status
from apps.wallet.models.payment import BankAccount

User = get_user_model()


class PayoutRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payout_requests')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='payout_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ], default='PENDING')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'PayoutRequest {self.id} by {self.user.email} - {self.status}'

class MoneyTransaction(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='money_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='money_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='money_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, max_length=255)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-MONEY{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MoneyTransaction, self).save(*args, **kwargs)

        
class BankTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)
    sender_model = models.ForeignKey(ContentType, related_name='bank_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='bank_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='bank_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='bank_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'wallet_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BankTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(BankTransactions, self).save(*args, **kwargs)


class TreasuryTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)
    sender_model = models.ForeignKey(ContentType, related_name='treasury_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='treasury_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='treasury_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='treasury_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'wallet_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TreasuryTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TreasuryTransactions, self).save(*args, **kwargs)


class ExpensesTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)

    sender_model = models.ForeignKey(ContentType, related_name='expenses_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='expenses_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='expenses_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='expenses_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'wallet_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'ExpensesTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ExpensesTransactions, self).save(*args, **kwargs)


class AppTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)

    sender_model = models.ForeignKey(ContentType, related_name='app_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='app_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='app_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='app_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AppTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AppTransactions, self).save(*args, **kwargs)



