import re
import random

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

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

SOCIAL_TYPE = (
    ('follow', _('follow')),
    ('share', _('share')),
    ('token', _('token')),
)

SOCIAL_SOURCE = (
    ('facebook', _('facebook')),
    ('twitter', _('twitter')),
    ('linkedin', _('linkedin')),
    ('telegram', _('telegram')),
    ('reddit', _('reddit')),
    ('youtube', _('youtube')),
    ('medium', _('medium')),
    ('steemit', _('steemit')),
    ('instagram', _('instagram')),
)

HOSTED = 'hosted'
POLONEIX = 'poloneix'
BINANCE = 'binance'
OKEX = 'okex'
# COIN_HOSTING = (

# )


def get_random():
    u_id = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                   for i in range(20))
    return u_id


class Coin(models.Model):
    """
    Model for coin details
    """
    COIN_HOSTING = (
        ('HOSTED', 'HOSTED'),
        ('POLONEIX', 'poloneix'),
        ('BINANCE', 'binance'),
        ('OKEX', 'okex')
    )
    coin_name = models.CharField(_('coin name'), max_length=255)
    coin_url = models.URLField(_('coin site URL'), null=True, blank=True)
    code = models.CharField(_('code'), max_length=25, unique=True)
    confirms = models.PositiveSmallIntegerField(_('confirms'))
    image = models.ImageField(_('image'), help_text=_(
        'Upload a 35X35 image for better experience'))

    coin_hosting_type = models.CharField(
        max_length=20, choices=COIN_HOSTING, default='HOSTED')
    to_btc = models.DecimalField(
        _('to BTC value'), max_digits=10, decimal_places=8, default=1.00000000)
    fee_percentage = models.DecimalField(
        _('fee percentage'), max_digits=5, decimal_places=2, default=0.00)
    type = models.PositiveSmallIntegerField(
        _('type'), choices=TYPE_CHOICES, default=CRYPTO)
    can_convert = models.BooleanField(
        _('can convert coin to another'), default=True)
    can_explore = models.BooleanField(_('can explore coins'), default=False)
    can_donate = models.BooleanField(_('can donate coins'), default=False)
    active = models.BooleanField(
        default=True, help_text=_('Disable this coin anytime'))
    display = models.BooleanField(
        default=False, help_text=_('Show/Hide this coin anytime'))
    min_deposit = models.DecimalField(
        max_digits=10, decimal_places=8, default=0)
    max_deposit = models.DecimalField(
        max_digits=10, decimal_places=8, default=0)
    vote_count = models.IntegerField(_('vote count'), default=0)

    class Meta:
        verbose_name = _('Coin')
        verbose_name_plural = _('Coins')

    def __str__(self):
        return self.coin_name


class CoinSetting(models.Model):
    """
    Model to save the coin setting for each user
    """
    user = models.ForeignKey(User, verbose_name=_(
        'user'), related_name='get_user_coin_settings', on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, verbose_name=_(
        'coin'), related_name='get_coin_settings', on_delete=models.CASCADE)
    enabled = models.BooleanField(_('enabled'), default=False)
    payment_address = models.CharField(_('payment address'), max_length=64)
    payment_mode = models.PositiveSmallIntegerField(
        _('payment mode'), choices=PAYMENT_MODE_CHOICES, default=TO_BALANCE)
    discount_percentage = models.DecimalField(
        _('discount field'), max_digits=6, decimal_places=2)
    maximum_per_transaction = models.DecimalField(
        _('maximum per transaction'), max_digits=6, decimal_places=2)
    currency = models.ForeignKey(Currency, verbose_name=_(
        'currency'), null=True, blank=True, on_delete=models.SET_NULL)

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
    wallet_from = models.CharField(
        _('wallet from address'), max_length=255, null=True, blank=True)
    wallet_to = models.CharField(
        _('wallet to address'), max_length=255, null=True, blank=True)

    def __str__(self):
        return 'Conversion request %s to %s' % (self.convert_from, self.convert_to)

    class Meta:
        verbose_name = _('Coin Conversion Request')
        verbose_name_plural = _('Coin Conversion Requests')


class WalletAddress(models.Model):
    """
    Model to save the coin addresses generated for each user
    """
    address = models.CharField(max_length=500, blank=True, default="")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Wallet(models.Model):
    """
    Model to save the coin wallet for each user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.ForeignKey(Coin, on_delete=models.CASCADE)
    addresses = models.ManyToManyField(WalletAddress)
    private = models.CharField(max_length=500, blank=True, default="")
    public = models.CharField(max_length=500, blank=True, default="")
    words = models.CharField(max_length=500, blank=True, default="")
    paymentid = models.CharField(max_length=500, blank=True, default="")

    def __str__(self):
        return self.user.username + '_' + self.name.code


class CoinRequest(models.Model):
    name = models.CharField(verbose_name=_(
        'name'), max_length=500, blank=True, default="")
    email = models.EmailField(verbose_name=_('email'), null=True, blank=True)
    coin_website = models.CharField(verbose_name=_(
        'coin website'), max_length=500, blank=True, default="")
    coin_url = models.URLField(verbose_name=_(
        'coin url'), null=True, blank=True)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.CharField(blank=False, max_length=200)
    balance = models.CharField(blank=True, max_length=20)
    currency = models.CharField(blank=True, max_length=20)
    transaction_id = models.CharField(blank=True, max_length=200)
    transaction_to = models.CharField(blank=True, max_length=200)
    message = models.CharField(blank=True, max_length=300)
    system_tx_id = models.CharField(max_length=50, default=get_random)
    activation_code = models.CharField(max_length=20, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class ClaimRefund(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    refund_sent_address = models.CharField(max_length=250)

    def __str__(self):
        return self.transaction.user.username


class Phases(models.Model):
    phase = models.CharField(verbose_name=_(
        'Voting_phase'), max_length=128, null=False)
    time_start = models.DateField(auto_now=False, auto_now_add=False)
    time_stop = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.phase


class NewCoin(models.Model):
    email = models.EmailField(verbose_name=_('email'))
    company_email = models.EmailField(verbose_name=_('comapny email'))
    first_name = models.CharField(verbose_name=_('first name'), max_length=30)
    last_name = models.CharField(verbose_name=_('last name'), max_length=30)
    contact_number = models.CharField(
        verbose_name=_('contact number'), max_length=20)
    secondary_number = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(verbose_name=_('coin name'),
                            max_length=30, unique=True)
    code = models.CharField(verbose_name=_('coin code'),
                            max_length=10, unique=True)
    website = models.URLField(_('website URL'), null=True, blank=True)
    # best_time_to_call = models.DateTimeField()
    logo_url = models.URLField(_('logo_url'), null=True, blank=True)
    hash_tags = models.CharField(verbose_name=_('hash tags'), max_length=100)
    twitter_handle = models.CharField(_('twitter handle'), max_length=20)
    fb_page = models.URLField(_('facebook page'), null=True, blank=True)
    twitter_page = models.URLField(_('twitter page'), null=True, blank=True)
    linkedin_page = models.URLField(_('linkedin page'), null=True, blank=True)
    telegram_page = models.URLField(_('telegram page'), null=True, blank=True)
    reddit_page = models.URLField(_('reddit page'), null=True, blank=True)
    vote_count = models.IntegerField(
        _('vote count'), default=0, null=True, blank=True)
    approved = models.BooleanField(default=False)
    phase = models.ForeignKey(Phases, blank=True, null=True, verbose_name=_(
        'voting_phase'), on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CoinVote(models.Model):
    user = models.ForeignKey(User, verbose_name=_(
        'user'), on_delete=models.CASCADE, null=True)
    coin = models.ForeignKey(NewCoin, verbose_name=_(
        'coin'), on_delete=models.CASCADE)
    type = models.CharField(choices=SOCIAL_TYPE, max_length=20, default='')
    source = models.CharField(choices=SOCIAL_SOURCE, max_length=20, default='')

    def __str__(self):
        return self.user.username+"_" + self.type+"_"+self.source


class PaybyName(models.Model):
    user = models.ForeignKey(User, verbose_name=_(
        'user paybyname'), on_delete=models.CASCADE)
    label = models.CharField(max_length=64, unique=True)

    def save(self, *args, **kwargs):
        temp = self.label
        temp = re.sub(r'\s+', '', temp)
        paybyname = "$PayTo-"+temp
        super(PaybyName, self).save(*args, **kwargs)


class CoPromotionURL(models.Model):
    url = models.URLField(_('copromotion url'))

    def __str__(self):
        return self.url


class CoPromotion(models.Model):
    coin = models.ForeignKey(NewCoin, verbose_name=_(
        'Coin name'), on_delete=models.CASCADE)
    urls = models.ManyToManyField(
        CoPromotionURL, verbose_name=_('CoPromotion URL'))

    def __str__(self):
        return self.coin.code


class WinnerCoins(models.Model):
    phase_name = models.CharField(max_length=64, unique=True)
    winner_coins = models.ForeignKey(NewCoin, verbose_name=_(
        'coin'), on_delete=models.CASCADE)


class EthereumToken(models.Model):
    coin_name = models.CharField(_('coin name'), max_length=255, blank=True)
    contract_symbol = models.CharField(max_length=30)
    contract_address = models.CharField(max_length=100)
    contract_abi = JSONField()
    image = models.ImageField(_('image'), help_text=_(
        'Upload a 35X35 image for better experience'), blank=True)
    display = models.BooleanField(
        default=False, help_text=_('Show/Hide this coin anytime'))

    def __str__(self):
        return self.contract_symbol


class EthereumTokenWallet(models.Model):
    """
    Model to save the coin wallet for each user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.ForeignKey(EthereumToken, on_delete=models.CASCADE)
    addresses = models.ManyToManyField(WalletAddress)
    private = models.CharField(max_length=500, blank=True, default="")
    public = models.CharField(max_length=500, blank=True, default="")
    words = models.CharField(max_length=500, blank=True, default="")
    paymentid = models.CharField(max_length=500, blank=True, default="")

    def __str__(self):
        return self.user.username + '_' + self.name.contract_symbol
