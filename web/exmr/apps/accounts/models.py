from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

from timezone_field import TimeZoneField
from django_countries.fields import CountryField

from apps.common.utils import send_email


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
    gender = models.PositiveSmallIntegerField(_('gender'), choices=GENDER_CHOICES, null=True, blank=True)
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
    referance_count = models.IntegerField(_('reference count'), null=True, default=0)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return u'%s' % self.since.strftime('%Y-%m-%d %H:%M')


@receiver(post_save, sender=Profile, dispatch_uid="update_merchant_id")
def update_merchant_id(sender, instance, **kwargs):
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


class ProfileActivation(models.Model):
    """
    Model to save the profile activation link details
    """
    user = models.ForeignKey(User, verbose_name=_('user'), on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=64)
    expired = models.BooleanField(default=False)

    def send_activation_email(self, site, request=None):
        """
        Send an activation email to the user associated with this
        ``ProfileActivation``.
        """

        activation_email_subject = _('Account Activation Link')
        activation_email_body = 'accounts/activation_email.txt'
        activation_email_html = 'accounts/activation_email.html'

        ctx_dict = {
            'user': self.user,
            'activation_key': self.activation_key,
            'site': site,
        }

        send_email(activation_email_subject, ctx_dict, self.user.email, email_template_txt=activation_email_body,
                   email_template_html=activation_email_html)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _('Profile Activation')
        verbose_name_plural = _('Profile Activations')


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
    buyer_or_seller = models.PositiveSmallIntegerField(_('buyer or seller'))

    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')

    def __str__(self):
        return '%s\'s feedback about %s' % (self.left_by.username, self.user.username)



class NewsLetter(models.Model):
    """
        Model to send newsletter to users
    """
    subject = models.CharField(_('subject'), max_length=200)
    is_active = models.BooleanField(default=False)
    content = RichTextField(verbose_name=_('content'),null=True,blank=True)

    def __str__(self):
        return self.subject
    #
    # @property
    # def newsletter_id(self):


ACCOUNT_TYPE = (
        ('google_authenticator', 'Google Authenticator/TOTP'),
    )

class TwoFactorAccount(models.Model):
    """
        model to hold totp two factor authentication details
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    account_name = models.CharField(max_length=128)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE)
    key = models.CharField(max_length=128)
    totp = models.CharField(max_length=128, null=True, verbose_name=_('Authentication Code'))

    def __str__(self):
        return self.account_name