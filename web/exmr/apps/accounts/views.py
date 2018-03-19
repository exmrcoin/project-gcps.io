from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import forms
from django.views.generic import CreateView, TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from apps.accounts.forms import SignUpForm
from apps.accounts.models import Profile, ProfileActivation
from apps.common.utils import generate_key




class SignUpView(CreateView):
    """
    View to signup a new user
    """
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:signup_complete')

    def form_valid(self, form):
        user = form.save()
        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')
        user.set_password(raw_password)  # This line will hash the password
        user.is_active = False
        user.save()
        profile, created = Profile.objects.get_or_create(user=user)
        profile.timezone = form.cleaned_data.get('timezone')
        profile.is_subscribed = form.cleaned_data.get('need_newsletter')
        profile.save()
        self.send_activation_mail(profile)
        return super(SignUpView, self).form_valid(form)

    def send_activation_mail(self, profile):

        """
        send activation mail
        :param profile:
        :return:
        """
        profile_activation, created = ProfileActivation.objects.get_or_create(user=profile.user)
        if created or profile_activation.expired:
            profile_activation.activation_key = generate_key(64)
            profile_activation.expired = False
        profile_activation.save()
        profile_activation.send_activation_email(get_current_site(self.request))


class SignUpCompleteView(TemplateView):

    template_name = 'accounts/signup_complete.html'


class ProfileActivationView(TemplateView):

    template_name = 'accounts/account_activated.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileActivationView, self).get_context_data(**kwargs)
        key = kwargs.get('key')
        try:
            act_obj = ProfileActivation.objects.get(activation_key=key)
        except ProfileActivation.DoesNotExist:
            context['status'] = _('Invalid account activation link')
        else:
            if act_obj.expired:
                context['status'] = _('Account activation link expired')
            else:
                act_obj.user.is_active = True
                act_obj.user.save()
                act_obj.expired = True
                act_obj.save()
                context['status'] = _('Account activated <br><p>Please <a href=/login>login</a><p>')
        return context
