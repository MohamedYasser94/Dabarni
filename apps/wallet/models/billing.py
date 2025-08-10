
from core.models.core import *
from helper.decorators import *
from helper.modelHelper import *
from helper.viewHelper import *

User = get_user_model()
class Purchase(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='purchase_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='purchase_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='purchase_owner', on_delete=models.SET_NULL, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    purchase_status = models.CharField(max_length=100, blank=True, null=True, choices=Purchase_Status,
                                       default='Pending')
    payment_status = models.CharField(max_length=100, blank=True, null=True, choices=Payment_Status, default='Pending')
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    due = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    quantity = models.IntegerField(default=0,null=True, blank=True,)
    status = models.CharField(max_length=100, choices=Active_Status, null=True, default='Active')
    serial_no = models.CharField(max_length=100, blank=True, null=True)
    tracking_no = models.CharField(max_length=100, blank=True, null=True)
    invoice_file = models.FileField(upload_to=get_file_path, null=True,blank=True)
    source = models.CharField(max_length=100, choices=Purchase_Source, default='Web', null=True, blank=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    purchase_date = models.DateField(null=True, blank=True,)
    due_date = models.DateField(null=True, blank=True,)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('view_order', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            order_code = f'PUR-{get_random_string(5).upper()}'
            serial_no = f'PUR-{get_random_string(8)}'
            self.serial_no = serial_no
            self.code = order_code
            self.slug = slugify(order_code)
        super(Purchase, self).save(*args, **kwargs)



class PurchaseItem(models.Model):
    receiver_model = models.ForeignKey(ContentType,related_name='item_purchase', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    item_model = models.ForeignKey(ContentType,related_name='item', on_delete=models.CASCADE, null=True, blank=True)
    item_id = models.PositiveIntegerField(null=True, blank=True)
    item = GenericForeignKey('item_model', 'item_id')
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE,blank=True,null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2,null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1,null=True, blank=True)
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=0,null=True, blank=True)
    name = models.CharField(max_length=100,null=True, blank=True)
    code = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            order_code = f'PUR-ITEM{get_random_string(5).upper()}'
            self.code = order_code
            self.slug = slugify(order_code)
        super(PurchaseItem, self).save(*args, **kwargs)



class Invoice(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='invoice_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='invoice_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='invoice_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    item_model = models.ForeignKey(ContentType, related_name='invoice_item', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    item_id = models.PositiveIntegerField(null=True, blank=True)
    item = GenericForeignKey('item_model', 'item_id')
    amount = models.FloatField(default=0.00, blank=True, null=True)
    title = models.CharField(null=True, blank=True, max_length=100)
    number = models.CharField(null=True, blank=True, max_length=100)
    url = models.URLField(max_length=100, blank=True, null=True)
    account_token = models.TextField( blank=True, null=True)
    merchant = models.CharField(max_length=100, blank=True, null=True)
    registration = models.CharField(max_length=100, blank=True, null=True)
    gateway_order = models.CharField(max_length=100, blank=True, null=True)
    gateway_transaction = models.CharField(max_length=100, blank=True, null=True)
    success = models.TextField( blank=True, null=True)
    message = models.TextField( blank=True, null=True)
    error = models.TextField( blank=True, null=True)
    reference = models.TextField( blank=True, null=True)
    is_success = models.BooleanField(default=False)
    dueDate = models.DateField(null=True, blank=True)
    status = models.CharField(choices=Invoice_Status , default='CURRENT', max_length=100)
    notes = models.TextField(null=True, blank=True)

    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    created_by = models.CharField(choices=Invoice_CreatedBy, default='STAFF', max_length=100)
    code = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} {self.code}'

    def get_absolute_url(self):
        return reverse('clinic:AdminCarInvoiceDetails', kwargs={'slug': self.slug})

    def get_backend_url(self):
        return reverse('shop:AdminOrderInvoice', kwargs={'slug': self.slug})

    def get_invoice_url(self):
        return reverse('shop:AdminOrderInvoice', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'INV-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Invoice, self).save(*args, **kwargs)


class Billing(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='bill_sender', on_delete=models.SET_NULL, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='bill_receiver', on_delete=models.SET_NULL,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='bill_owner', on_delete=models.SET_NULL, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    due = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    transaction_type = models.CharField(choices=Transaction_Money_Mode, max_length=100,default='Cash')
    transaction_method = models.CharField(choices=Transaction_Method, max_length=100,default='Cash')
    pay_date = models.DateField(null=True, blank=True)
    next_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=100, blank=True, null=True, choices=Payment_Status, default='Pending')
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active')
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'billing'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['cases']

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BILL-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Billing, self).save(*args, **kwargs)
