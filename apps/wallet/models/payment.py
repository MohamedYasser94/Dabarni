from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import Active_Status, Payment_Gateway, Payment_Status, Payment_Methods, Public_Status
from helper.viewHelper import get_file_path

User = get_user_model()


class PaymentGateway(models.Model):
    name = models.CharField(max_length=100,choices=Payment_Gateway, null=True, blank=True)
    gateway_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    storage = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    code = models.CharField(unique=True, max_length=100, )
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_image(self):
        try:
            return self.image.url
        except:
            return None

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PaymentGateway-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(PaymentGateway, self).save(*args, **kwargs)

class PaymentGatewaySetting(models.Model):
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE, null=True, blank=True)
    setting_name = models.CharField(max_length=100, blank=True, null=True)
    setting_key = models.CharField(max_length=100, blank=True, null=True)
    setting_value = models.CharField(max_length=100, blank=True, null=True)
    setting_secret = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    code = models.CharField(unique=True, max_length=100, )
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.setting_name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PaymentGatewaySetting-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(PaymentGatewaySetting, self).save(*args, **kwargs)


class SubscriptionPlan(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    ad_limit = models.PositiveIntegerField()  # Max ads per month
    featured_ad_limit = models.PositiveIntegerField(default=0)
    duration_days = models.PositiveIntegerField()  # e.g., 30 for monthly
    is_active = models.CharField(max_length=20, choices=Public_Status, default='No', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self):
        if not self.code and not self.slug:
            code = f'SubscriptionPlan{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SubscriptionPlan, self).save()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.title}"

    def save(self):
        if not self.code and not self.slug:
            code = f'Subscription{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Subscription, self).save()


class SubscriptionPayment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)  # e.g., 'Credit Card', 'PayPal'
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount} {self.currency}"

    def save(self):
        if not self.code and not self.slug:
            code = f'SubscriptionPayment{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SubscriptionPayment, self).save()

class Payment(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='payment_sender', on_delete=models.SET_NULL, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='payment_receiver', on_delete=models.SET_NULL, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='payment_owner', on_delete=models.SET_NULL, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    amount = models.FloatField(default=0.00, blank=True, null=True)
    fee = models.FloatField(default=0.00, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    api_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    payment_status = models.CharField(max_length=100, choices=Payment_Status, null=True, blank=True)
    payment_method = models.CharField(max_length=100, choices=Payment_Methods, null=True, blank=True)
    payment_gateway = models.CharField(max_length=100,choices=Payment_Gateway, null=True, blank=True)
    gateway_order = models.CharField(max_length=100, blank=True, null=True)
    gateway_transaction = models.CharField(max_length=100, blank=True, null=True)
    pending = models.BooleanField(default=False)
    success = models.BooleanField(default=False)
    code = models.CharField(unique=True, max_length=100, )
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.code
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Payment-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(Payment, self).save(*args, **kwargs)

class Banks(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    code = models.CharField(unique=True, max_length=100, )
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_image(self):
        try:
            return self.image.url
        except:
            return None

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Banks-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(Banks, self).save(*args, **kwargs)


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=100, blank=True, null=True, )
    account_number = models.CharField(max_length=100, blank=True, null=True, )
    iban = models.CharField(max_length=100, blank=True, null=True, )
    swift_code = models.CharField(max_length=100, blank=True, null=True, )
    account_name = models.CharField(max_length=100, blank=True, null=True, )
    country = models.CharField(max_length=100, blank=True, null=True, )
    account_email = models.CharField(max_length=100, blank=True, null=True, )
    crypto_address = models.CharField(max_length=100, blank=True, null=True, )
    description = models.TextField(blank=True, null=True)
    default_account = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    code = models.CharField(unique=True, max_length=100, )
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bank_name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BankAccount-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(BankAccount, self).save(*args, **kwargs)