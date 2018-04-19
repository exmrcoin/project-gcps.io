from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from apps.common.models import Currency

CRYPTO = 0
RIPPLE = 1
ETHER_TOKENS = 2
FIAT = 3

TYPE_CHOICES = (
    (CRYPTO, _('Crypto')),
    (RIPPLE, _('Ripple')),
    (ETHER_TOKENS, _('Ether tokens')),
    (FIAT, _('Fiat')),
)

TO_BALANCE = 0
ASAP = 1
NIGHTLY = 2
TO_BALANCE_CONVERT = 3
ASAP_CONVERT = 4

PAYMENT_MODE_CHOICES = (
    (TO_BALANCE, _('To Balance')),
    (ASAP, _('ASAP')),
    (NIGHTLY, _('Nightly')),
    (TO_BALANCE_CONVERT, _('To Balance + Convert')),
    (ASAP_CONVERT, _('ASAP + Convert'))
)


class Coin(models.Model):
    """
    Model for coin details
    """
    coin_name = models.CharField(_('coin name'), max_length=255)
    coin_url = models.URLField(_('coin site URL'), null=True, blank=True)
    code = models.CharField(_('code'), max_length=25, unique=True)
    confirms = models.PositiveSmallIntegerField(_('confirms'))
    image = models.ImageField(_('image'), help_text=_('Upload a 35X35 image for better experience'))
    to_btc = models.DecimalField(_('to BTC value'), max_digits=10, decimal_places=8, default=1.00000000)
    fee_percentage = models.DecimalField(_('fee percentage'), max_digits=5, decimal_places=2, default=0.00)
    type = models.PositiveSmallIntegerField(_('type'), choices=TYPE_CHOICES, default=CRYPTO)
    can_convert = models.BooleanField(_('can convert coin to another'), default=True)
    can_explore = models.BooleanField(_('can explore coins'), default=False)
    can_donate = models.BooleanField(_('can donate coins'), default=False)
    active = models.BooleanField(default=True, help_text=_('Disable this coin anytime'))
    min_deposit = models.DecimalField(max_digits=10, decimal_places=8, default=0)
    max_deposit = models.DecimalField(max_digits=10, decimal_places=8, default=0)

    class Meta:
        verbose_name = _('Coin')
        verbose_name_plural = _('Coins')

    def __str__(self):
        return self.coin_name


class CoinVote(models.Model):
    """
    Model for coin votes
    """
    coin = models.ForeignKey(Coin, verbose_name=_('coin'), related_name='get_coin_votes', on_delete=models.CASCADE)
    vote_count = models.IntegerField(_('vote count'))

    class Meta:
        verbose_name = _('Coin Vote')
        verbose_name_plural = _('Coin Votes')

    def __str__(self):
        return self.coin.coin_name


class CoinSetting(models.Model):
    """
    Model to save the coin setting for each user
    """
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='get_user_coin_settings', on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, verbose_name=_('coin'), related_name='get_coin_settings', on_delete=models.CASCADE)
    enabled = models.BooleanField(_('enabled'), default=False)
    payment_address = models.CharField(_('payment address'), max_length=64)
    payment_mode = models.PositiveSmallIntegerField(_('payment mode'), choices=PAYMENT_MODE_CHOICES, default=TO_BALANCE)
    discount_percentage = models.DecimalField(_('discount field'), max_digits=6, decimal_places=2)
    maximum_per_transaction = models.DecimalField(_('maximum per transaction'), max_digits=6, decimal_places=2)
    currency = models.ForeignKey(Currency, verbose_name=_('currency'), null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '%s setting for %s' % (self.coin, self.user)


class CoinConvertRequest(models.Model):
    """
    Model to save all the coin conversion requests
    """
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='user_conversion_requests',
                             null=True, blank=True, on_delete=models.SET_NULL)
    convert_from = models.ForeignKey(Coin, verbose_name=_('convert from coin'),
                                     related_name='from_conversions', on_delete=models.CASCADE)
    convert_to = models.ForeignKey(Coin, verbose_name=_('convert to coin'), related_name='to_conversions',
                                   on_delete=models.CASCADE)
    wallet_from = models.CharField(_('wallet from address'), max_length=255, null=True, blank=True)
    wallet_to = models.CharField(_('wallet to address'), max_length=255, null=True, blank=True)

    def __str__(self):
        return 'Conversion request %s to %s' % (self.convert_from, self.convert_to)

    class Meta:
        verbose_name = _('Coin Conversion Request')
        verbose_name_plural = _('Coin Conversion Requests')
