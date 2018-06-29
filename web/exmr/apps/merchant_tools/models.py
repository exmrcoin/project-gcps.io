from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
# Create your models here.


class ButtonMaker(models.Model):
    merchant_id = models.CharField(
        verbose_name=_('merchant id'), max_length=128)
    item_name = models.CharField(max_length=128, null=False)
    item_amount = models.CharField(max_length=128, null=False)
    item_number = models.CharField(max_length=128, null=False)
    item_qty = models.CharField(max_length=128, null=False)
    buyer_qty_edit = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=128, null=False)
    tax_amount = models.CharField(max_length=128, null=False)
    allow_shipping_cost = models.BooleanField(default=False)
    shipping_cost = models.CharField(max_length=128, null=False)
    shipping_cost_add = models.CharField(max_length=128, null=False)
    success_url_link = models.CharField(max_length=128, null=False)
    cancel_url_link = models.CharField(max_length=128, null=False)
    ipn_url_link = models.CharField(max_length=128, null=False)
    btn_image = models.ForeignKey('ButtonImage', on_delete=models.CASCADE)
    allow_buyer_note = models.BooleanField(default=False)

    def __str__(self):
        return self.item_name


class ButtonImage(models.Model):
    label = models.CharField(max_length=128, null=False)
    btn_img = models.ImageField(upload_to='button_maker/')

    def __str__(self):
        return self.label

    def image_tag(self):
        return mark_safe('<img src="/directory/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = 'Image'
