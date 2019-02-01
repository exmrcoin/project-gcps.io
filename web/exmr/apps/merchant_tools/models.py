import datetime

from datetime import datetime, timedelta

from ckeditor.fields import RichTextField, RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingField

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


from apps.coins.models import Coin, EthereumToken
from apps.merchant_tools import random_primary
from apps.accounts.models import User, Profile

# Create your models here.


class ButtonMaker(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.DecimalField(max_digits=20, decimal_places=2, null=False)
    buyer_qty_edit = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=128, null=False)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    allow_shipping_cost = models.BooleanField(default=False)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    shipping_cost_add = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    success_url_link = models.URLField(max_length=128, blank=True, null=True)
    cancel_url_link = models.URLField(max_length=128, blank=True, null=True)
    ipn_url_link = models.URLField(max_length=128, blank=True, null=True)
    btn_image = models.ForeignKey('ButtonImage', on_delete=models.CASCADE)
    allow_buyer_note = models.BooleanField(default=False)

    def __str__(self):
        return self.item_name

class SimpleButtonMaker(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_description = models.CharField(max_length=500, null=False)
    invoice_number = models.CharField(max_length=128, null=True)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    allow_shipping_cost = models.BooleanField(default=False)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    success_url_link = models.URLField(max_length=128, blank=True, null=True)
    cancel_url_link = models.URLField(max_length=128, blank=True, null=True)
    ipn_url_link = models.URLField(max_length=128, blank=True, null=True)
    btn_image = models.ForeignKey('ButtonImage', on_delete=models.CASCADE)
    

    def __str__(self):
        return self.item_name

class DonationButtonMaker(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    donation_name = models.CharField(max_length=128, null=False)
    donation_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True)
    item_number = models.CharField(max_length=128, null=False)
    allow_donator_to_adjust_amount = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=128, null=False)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    collect_shipping_address = models.BooleanField(default=False)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    success_url_link = models.URLField(max_length=128, blank=True, null=True)
    cancel_url_link = models.URLField(max_length=128, blank=True, null=True)
    ipn_url_link = models.URLField(max_length=128, blank=True, null=True)
    btn_image = models.ForeignKey('ButtonImage', on_delete=models.CASCADE)
    allow_donor_note = models.BooleanField(default=False)

    def __str__(self):
        return self.donation_name

class ButtonImage(models.Model):
    label = models.CharField(max_length=128, null=False)
    btn_img = models.ImageField(upload_to='button_maker/')

    def __str__(self):
        return self.label

    def image_tag(self):
        return mark_safe('<img src="/directory/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = 'Image'


class CryptoPaymentRec(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.CharField(max_length=128, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.CharField(max_length=128, null=False)
    invoice_number = models.CharField(max_length=128, null=False)
    unique_id = models.CharField(max_length=128, null=False)

    tax_amount = models.CharField(max_length=128, null=False)
    shipping_cost = models.CharField(max_length=128, null=False)
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    email_addr = models.CharField(max_length=128, null=False)
    addr_l1 = models.CharField(max_length=128, null=False)
    addr_l2 = models.CharField(max_length=128, null=False)
    country = models.CharField(max_length=128, null=False)
    city = models.CharField(max_length=128, null=False)
    state = models.CharField(max_length=128, null=False)
    zipcode = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=128, null=False)
    buyer_note = models.CharField(max_length=128, blank=True, null=True)
    selected_coin = models.ForeignKey(Coin, on_delete=models.CASCADE, null = True)
    selected_erc_token = models.ForeignKey(EthereumToken, on_delete=models.CASCADE, null = True)
    wallet_address = models.CharField(max_length=128, null=False)

    def __str__(self):
        return self.item_name +"_"+ Profile.objects.get(merchant_id = self.merchant_id).user.username


class MercSidebarTopic(models.Model):
    """
    Model to save frequently asked questions
    """
    merc_side_topic = models.CharField(max_length=512)

    def __str__(self):
        return self.merc_side_topic


class MercSidebarSubTopic(models.Model):
    """
    Model to save help sidebar topics and their answers
    """
    main_topic = models.ForeignKey(MercSidebarTopic, on_delete=models.CASCADE)
    sub_topic = models.CharField(max_length=64)
    help_answer = RichTextUploadingField()
    order_index = models.IntegerField()
    slug = models.SlugField(default=slugify(sub_topic))

    def __str__(self):
        return self.sub_topic

    def save(self, *args, **kwargs):
        self.slug = slugify(self.sub_topic)
        super(MercSidebarSubTopic, self).save(*args, **kwargs)


class URLMaker(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_name = models.CharField(max_length=128, null=False)
    item_desc = models.CharField(max_length=512, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    invoice_number = models.CharField(max_length=128, null=False)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default= 0)
    ipn_url_link = models.CharField(max_length=128, blank=True, null=True)
    URL_link = models.CharField(max_length=256, null=False)

    def __str__(self):
        return self.item_name


class POSQRMaker(models.Model):
    
    def four_hour_hence():
        return timezone.now() + timezone.timedelta(hours=12)

    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_desc = models.CharField(max_length=512, blank=True, null=True)
    item_amount = models.CharField(max_length=128, null=False)
    currency = models.ForeignKey(Coin, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=128, null=False)
    custom_field = models.CharField(max_length=128, blank=True, null=True)
    URL_link = models.CharField(max_length=256, null=False)
    time_limit = models.CharField(max_length=128, null=False)

    def __str__(self):
        return self.item_desc


class MultiPayment(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128, null = True, blank=True)
    paid_in = models.ForeignKey(Coin, on_delete=models.PROTECT, null = True, blank=True)
    paid_in_erc = models.ForeignKey(EthereumToken, on_delete=models.PROTECT, null = True, blank=True)
    payment_address = models.CharField(max_length=512, null=False)
    paid_amount = models.CharField(max_length=512, null=False)
    eq_usd = models.CharField(max_length=512, blank=True, null=True)
    paid_date = models.DateTimeField(blank=True, null=True, auto_now_add=True, editable = True)
    attempted_usd = models.CharField(max_length=512, default=0)
    recieved_amount = models.CharField(max_length=512, default=0)
    recieved_usd = models.CharField(max_length=512, default=0)
    paid_unique_id = models.CharField(max_length=512, blank=True, null=True)
    transaction_id = models.CharField(max_length=64, null=False)

    def __str__(self):
        return str(self.paid_in)


class ButtonInvoice(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    invoice_number = models.CharField(max_length=128, null=False)
    unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.DecimalField(max_digits=20, decimal_places=2, null=False)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    buyer_note = models.CharField(max_length=128, null=True)
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    email_addr = models.CharField(max_length=128, null=False)
    addr_l1 = models.CharField(max_length=128, null=False)
    addr_l2 = models.CharField(max_length=128, null=False)
    country = models.CharField(max_length=128, null=False)
    city = models.CharField(max_length=128, null=False)
    state = models.CharField(max_length=128, null=False)
    zipcode = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=128, null=False)
    URL_link = models.CharField(max_length=256, null=False)

    def __str__(self):
        return self.item_name + "_"+ self.unique_id

class DonationButtonInvoice(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    invoice_number = models.CharField(max_length=128, null=False)
    unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.DecimalField(max_digits=20, decimal_places=2, null=False)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    buyer_note = models.CharField(max_length=128, null=True)
    first_name = models.CharField(max_length=128, null=True, default='')
    last_name = models.CharField(max_length=128, null=True)
    email_addr = models.CharField(max_length=128, null=True)
    addr_l1 = models.CharField(max_length=128, null=True)
    addr_l2 = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128, null=True)
    state = models.CharField(max_length=128, null=True)
    zipcode = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=128, null=True)
    URL_link = models.CharField(max_length=256, null=True)

    def __str__(self):
        return self.item_name + "_"+ self.unique_id

class SimpleButtonInvoice(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    invoice_number = models.CharField(max_length=128, null=False)
    unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.DecimalField(max_digits=20, decimal_places=2, null=False)
    tax_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    buyer_note = models.CharField(max_length=128, null=True)
    first_name = models.CharField(max_length=128, null=True, default='')
    last_name = models.CharField(max_length=128, null=True)
    email_addr = models.CharField(max_length=128, null=True)
    addr_l1 = models.CharField(max_length=128, null=True)
    addr_l2 = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128, null=True)
    state = models.CharField(max_length=128, null=True)
    zipcode = models.CharField(max_length=128, null=True)
    phone = models.CharField(max_length=128, null=True)
    URL_link = models.CharField(max_length=256, null=True)
    payment_status = models.CharField(max_length=256, default="PENDING")

    def __str__(self):
        return self.item_name + "_"+ self.unique_id

class ButtonItem(models.Model):
    item_unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_discount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128, null = True)
    item_tax = models.DecimalField(
        max_digits=20, decimal_places=2, null=False, default= 0)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    shipping_cost_add = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    
    def __str__(self):
        return self.item_name

class SimpleButtonItem(models.Model):
    item_unique_id = models.CharField(max_length=128, null=False, unique=True)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=False)
    item_discount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, default = 0)
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128, null = True)
    item_tax = models.DecimalField(
        max_digits=20, decimal_places=2, null=False, default= 0)
    shipping_cost = models.DecimalField(
        max_digits=20, decimal_places=2,  null=True, default = 0)
    
    def __str__(self):
        return self.item_name

class MerchantPaymentWallet(models.Model):
    address = models.CharField(max_length=200, blank=True)
    private = models.CharField(max_length=200, blank=True)
    merchant = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, blank=True)
    initiated_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    timed_out = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=False, default= 0)
    unique_id = models.CharField(max_length=128, null=False)
    market_rate = models.CharField(max_length=128, default="0")

    def __str__(self):
        return self.merchant.username