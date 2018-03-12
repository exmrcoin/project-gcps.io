import pytz

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.common_timezones]


class SignUpForm(UserCreationForm):

    email = forms.EmailField()
    confirm_email = forms.EmailField()
    timezone = forms.ChoiceField(choices=CHOICES)
    need_newsletter = forms.BooleanField(required=False)
    accept_terms_and_conditions = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'confirm_email']

    def clean_confirm_email(self):
        if self.cleaned_data.get('email') != self.cleaned_data.get('confirm_email'):
            return forms.ValidationError(_("Emails doesn't match"))
        return self.cleaned_data.get('confirm_email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def clean_accept_terms_and_conditions(self):
        if not self.cleaned_data.get('accept_terms_and_conditions'):
            raise forms.ValidationError(_('Please accept the terms and conditions'))
        return self.cleaned_data.get('accept_terms_and_conditions')
