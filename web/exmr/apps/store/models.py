from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from apps.coins.models import Coin


class StoreCategory(models.Model):
    """
    Model for store category
    """
    name = models.CharField(_('name'), max_length=255)
    publish = models.BooleanField(_('publish'), default=True)
    slug = models.SlugField(_('slug'), auto_created=True)
    image = models.FileField(verbose_name=_('image'), upload_to='store/category',
                             help_text='Add svg image of size 2137x2138 ')

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super(StoreCategory, self).save(*args, **kwargs)


class Store(models.Model):
    """
    Model for store information
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='get_user_stores', verbose_name=_('user'))
    store_name = models.CharField(_('store name'), max_length=255)
    store_url = models.URLField(_('store url'))
    category = models.ForeignKey(StoreCategory, verbose_name=_('category'), related_name='get_store_category', on_delete=models.CASCADE)
    crypto_processor = models.CharField(_('crypto processor'), max_length=255)
    store_email = models.EmailField(_('store email'))
    keywords = models.CharField(_('keywords'), max_length=255, null=True, blank=True)
    banner_image_url = models.URLField(_('banner image url'))
    is_approved = models.BooleanField(_('is approved'), default=False)
    votes = models.IntegerField(default=0)
    percent = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')

    def get_absolute_url(self):
        return reverse('store:store-item', kwargs={'slug': self.category.slug})

    def __str__(self):
        return self.store_name

class StorePaymentRec(models.Model):
    store_id = models.CharField(max_length=10, null=False)
    item_amount = models.CharField(max_length=128, null=False)
    
    unique_id = models.CharField(max_length=128, null=False)

    
    first_name = models.CharField(max_length=128, null=False)
    last_name = models.CharField(max_length=128, null=False)
    email_addr = models.CharField(max_length=128, null=False)
    
    selected_coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    wallet_address = models.CharField(max_length=128, null=False)

    def __str__(self):
        return self.item_name +"_"+ Profile.objects.get(merchant_id = self.merchant_id).user.username

class Rating(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE, null=True)
    store = models.ForeignKey(Store, related_name='store', on_delete=models.CASCADE, null=True)
    votes = models.IntegerField()
    has_voted = models.BooleanField()


    def __str__(self):
        return str(self.votes)