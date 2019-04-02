import re

import pytz

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q

from apps.accounts.models import Profile, Address, KYC

CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]

MALE = 0
FEMALE = 1
OTHER = 2

GENDER_CHOICES = [
    ('', '---Please select ---'),
    (MALE, _('Male')),
    (FEMALE, _('Female')),
    (OTHER, _('Other/Prefer Not to say')),
]


DATE_FORMAT_CHOICES = [('02-10-2018', _('02-10-2018')),
                       ('02/10/2018', _('02/10/2018'))]


TIME_FORMAT_CHOICES = [('02:00', _('02:00')),
                       ('02:00:00', _('02:00:00'))]


class SignUpForm(UserCreationForm):

    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    confirm_email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    timezone = forms.ChoiceField(choices=CHOICES)
    need_newsletter = forms.BooleanField(required=False)
    accept_terms_and_conditions = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'confirm_email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Please use a different email address.')
        return email.lower()

    def clean_confirm_email(self):
        email = self.cleaned_data.get('confirm_email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Please use a different email address.')
        return email.lower()


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def clean_accept_terms_and_conditions(self):
        if not self.cleaned_data.get('accept_terms_and_conditions'):
            raise forms.ValidationError(_('Please accept the terms and conditions'))
        return self.cleaned_data.get('accept_terms_and_conditions')

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        try:
            if cleaned_data['email'] != cleaned_data['confirm_email']:
                raise forms.ValidationError("Your emails don't match")
        except:
            pass
        return cleaned_data


class UpdateBasicProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    confirm_email = forms.EmailField(required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    timezone = forms.ChoiceField(choices=CHOICES)
    date_format = forms.ChoiceField(choices=DATE_FORMAT_CHOICES)
    time_format = forms.ChoiceField(choices=TIME_FORMAT_CHOICES)

    class Meta:
        model = Profile
        fields = ['gender', 'timezone', 'date_format', 'time_format', 'email', 'confirm_email']

    def __init__(self, *args, **kwargs):
        super(UpdateBasicProfileForm, self).__init__(*args, **kwargs)
        self.fields['timezone'].widget.attrs['class'] = 'form-control select-view'
        self.fields['email'].widget.attrs['class'] = 'form-control text-view'
        self.fields['confirm_email'].widget.attrs['class'] = 'form-control text-view'
        self.fields['gender'].widget.attrs['class'] = 'form-control select-view'
        self.fields['date_format'].widget.attrs['class'] = 'datepicker form-control select-view  w100'
        self.fields['time_format'].widget.attrs['class'] = 'timepicker form-control select-view'

    def clean_confirm_email(self):
        cleaned_data = super(UpdateBasicProfileForm, self).clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirm_email")
        if email and confirm_email:
            if email != confirm_email:
                raise forms.ValidationError("Emails do not match.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError(u'Please use a different email address.')
        return email


class PublicInfoForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['public_name', 'public_email', 'public_url', 'use_gravatar']


class AddressForm(forms.ModelForm):

    phone_number = forms.CharField()

    class Meta:
        model = Address
        fields = ['address_name', 'first_name', 'last_name', 'address_line_1',
                  'address_line_2', 'country', 'city', 'state', 'postal_code', 'phone_number',
                  'is_default'
                  ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        rule = re.compile('^\+(?:[0-9]●?){6,14}[0-9]$')
        if not rule.search(phone_number):
            raise forms.ValidationError(_('Invalid mobile number.'))
        return phone_number


class LoginSecurityForm(forms.ModelForm):

    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = ['password', 'pgp_gpg_public_key', 'current_password', 'confirm_password',
                  'two_factor_auth', 'email_confirmation_transaction']

    def clean_two_factor_auth(self):
        auth_method = self.cleaned_data.get('two_factor_auth')
        if not self.instance.user.get_user_2fa.exists():
            raise forms.ValidationError('Please add a 2FA device to enable this method')
        return auth_method

    def clean_current_password(self):
        pswd = self.cleaned_data.get('current_password')
        if self.cleaned_data.get('current_password') or \
         self.cleaned_data.get('current_password') or \
         self.cleaned_data.get('password'): 
            if not authenticate(username=self.instance.user.username, password=pswd):
                raise forms.ValidationError('Please enter valid current password')
        return pswd

    def clean_confirm_password(self):
        cpswd = self.cleaned_data.get('confirm_password')
        if self.cleaned_data.get('current_password') or \
         self.cleaned_data.get('current_password') or \
         self.cleaned_data.get('password'):
            pswd = self.cleaned_data.get('password')
            if cpswd != pswd:
                raise forms.ValidationError('Passwords you entered are not matching ')
        return cpswd



class IPNSettingsForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['ipn_secret', 'ipn_url', 'mail_on_new_payment_init', 'mail_on_new_fund_receive', 'mail_on_fund_sent',
                  'mail_on_deposit_receive', 'mail_on_positive_feedback', 'status_email', 'receive_sms', 'phone']


class CustomPasswordResetForm(PasswordResetForm):

    username = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    def clean(self):
        if not self.cleaned_data.get('username'):
            raise forms.ValidationError(_('Either username or email needs to be provided'))
        else:
            username = self.cleaned_data.get('username')
            user = User.objects.filter(Q(username=username, is_active=True) | Q(email=username, is_active=True)).first()
        if not user:
            raise forms.ValidationError(_('User not found'))

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = User._default_manager.filter(**{
            '%s__iexact' % User.get_email_field_name(): email,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        username = self.cleaned_data.get('username')
        user = User.objects.filter(Q(username=username, is_active=True) | Q(email=username, is_active=True)).first()
        if user:
            email = user.email
            for user in self.get_users(email):
                if not domain_override:
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                else:
                    site_name = domain = domain_override
                context = {
                    'email': email,
                    'domain': domain,
                    'site_name': site_name,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'user': user,
                    'token': token_generator.make_token(user),
                    'protocol': 'https' if use_https else 'http',
                }
                if extra_email_context is not None:
                    context.update(extra_email_context)
                self.send_mail(
                    user, subject_template_name, email_template_name, context, 
                    from_email,email, html_email_template_name=html_email_template_name,
                )


class KYCForm(forms.ModelForm):

    class Meta:
        model = KYC
        fields = ['full_name', 'address_line_1', 'address_line_2',\
                  'id_number', 'id_proof', 'selfie', 'ssn']

    def __init__(self, *args, **kwargs):
        super(KYCForm, self).__init__(*args, **kwargs)
        self.fields['address_line_1'].widget.attrs['class'] = 'form-control'
        self.fields['address_line_2'].widget.attrs['class'] = 'form-control'
        self.fields['id_number'].widget.attrs['class'] = 'form-control'
        self.fields['full_name'].widget.attrs['class'] = 'form-control'
        self.fields['id_proof'].widget.attrs['class'] = 'form-control'
        self.fields['selfie'].widget.attrs['class'] = 'form-control'
        self.fields['ssn'].widget.attrs['class'] = 'form-control'
