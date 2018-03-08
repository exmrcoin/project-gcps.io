from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string


from timezone_field import TimeZoneField
from django_countries.fields import CountryField


MALE = 0
FEMALE = 1
OTHER = 2

GENDER_CHOICES = (
    (MALE, _('Male')),
    (FEMALE, _('Female')),
    (OTHER, _('Other/Prefer Not to say')),
)

EMAIL = 0
TREZOR = 1
TWO_FA_ACCOUNT = 2
NONE = 3

BUYER = 0
SELLER = 1

USER_TYPE = (
    (BUYER, _('Buyer')),
    (SELLER, _('Seller')),
)

TWO_FACTOR_AUTH_CHOICES = (
    (EMAIL, _('Email')),
    (TREZOR, _('Trezor Login')),
    (TWO_FA_ACCOUNT, _('2FA Account')),
    (NONE, _('None')),
)


class Profile(models.Model):
    """
    Model to save user profile details
    """
    user = models.OneToOneField(User, verbose_name=_('user'), related_name='get_profile', on_delete=models.CASCADE)
    gender = models.PositiveSmallIntegerField(_('gender'), choices=GENDER_CHOICES, default=OTHER)
    user_type = models.PositiveSmallIntegerField(_('user type'), choices=USER_TYPE, default=BUYER)
    timezone = TimeZoneField(verbose_name=_('timezone'), default='UTC')
    public_name = models.CharField(_('public name'), max_length=255, null=True, blank=True)
    public_email = models.EmailField(_('public email'), null=True, blank=True)
    public_url = models.URLField(_('public URL'), null=True, blank=True)
    merchant_id = models.CharField(_('merchant id'), max_length=32, null=True, blank=True, unique=True, editable=False)
    date_format = models.CharField(_('date format'), max_length=255, null=True, blank=True)
    time_format = models.CharField(_('time format'), max_length=255, null=True, blank=True)
    use_gravatar = models.BooleanField(_('use gravatar'), default=False)
    pgp_gpg_public_key = models.TextField(_('PGP/GPG public key'), null=True, blank=True)
    two_factor_auth = models.PositiveSmallIntegerField(_('2FA authentication'),
                                                       choices=TWO_FACTOR_AUTH_CHOICES, default=EMAIL)
    email_confirmation_transaction = models.BooleanField(_('email confirmation send/withdrawal'), default=True)
    is_subscribed = models.BooleanField(_('is subscribed'), default=False)


    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=Profile, dispatch_uid="update_merchant_id")
def update_stock(sender, instance, **kwargs):
    """
    Signal to create merchant id for profiles
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if not instance.merchant_id:
        instance.merchant_id = get_random_string(length=32)
        instance.save()


class Address(models.Model):
    """
    Model to save address details
    """
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='get_user_addresses', on_delete=models.CASCADE)
    address_name = models.CharField(_('saved address name'), max_length=255)
    is_default = models.BooleanField(_('is default'), default=False)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    address_line_1 = models.CharField(_('address line 1'), max_length=255)
    address_line_2 = models.CharField(_('address line 2'), max_length=255, null=True, blank=True)
    country = CountryField(verbose_name=_('country'), default='US')
    city = models.CharField(_('city'), max_length=255)
    state = models.CharField(_('state'), max_length=255)
    postal_code = models.CharField(_('postal code'), max_length=255)
    phone_number = models.CharField(_('phone_number'), max_length=255)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return self.address_name


class Feedback(models.Model):
    """
    Model to save the feedback for users
    """
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='get_all_feedback', on_delete=models.CASCADE)
    rating = models.FloatField(_('rating'))
    comment = models.TextField(_('comment'), null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    left_by = models.ForeignKey(User, verbose_name=_('left by'), on_delete=models.CASCADE, null=True, blank=True)
    blocked = models.BooleanField(default=False)
    buyer_or_seller = models.PositiveSmallIntegerField(_(''))

    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')

    def __str__(self):
        return '%s\'s feedback about %s' % (self.left_by.username, self.user.username)

