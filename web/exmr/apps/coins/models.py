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
    code = models.CharField(_('code'), max_length=25)
    confirms = models.PositiveSmallIntegerField(_('confirms'))
    image = models.ImageField(_('image'))
    type = models.PositiveSmallIntegerField(_('type'), choices=TYPE_CHOICES, default=CRYPTO)

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
