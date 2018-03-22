from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template.context_processors import request
from django.views.generic import CreateView, TemplateView, FormView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from apps.accounts.forms import SignUpForm, UpdateBasicProfileForm
from apps.accounts.models import Profile, ProfileActivation
from apps.common.utils import generate_key
from .forms import CHOICES
import datetime as dt





class SignUpView(CreateView):
    """
    View to signup a new user
    """
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:signup_complete')

    def form_valid(self, form):
        user = form.save()
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


class AccountSettings(FormView):
    form_class = UpdateBasicProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')

    def get_initial(self):
        initial = super(AccountSettings, self).get_initial()
        user = get_object_or_404(User, username=self.request.user)
        # try:
        user_profile = Profile.objects.get(user_id=user.id)
        # except user_profile.DoesNotExist:
        #     user_profile = None
        initial['email'] = self.request.user.email
        initial['confirm_email'] = self.request.user.email
        initial['timezone'] = user_profile.timezone
        date_time = user_profile.date_time
        date = date_time.strftime('%m/%d/%Y')
        time = date_time.strftime('%H:%M')
        initial['date_format'] = date
        initial['time_format'] = time
        initial['merchant_id'] = user_profile.merchant_id
        initial['gender'] = user_profile.gender
        return initial

    def get_context_data(self, **kwargs):
        obj = self.get_initial()
        context = super(AccountSettings, self).get_context_data(**kwargs)
        context['merchant_id'] = obj['merchant_id']
        return context

    def form_valid(self, form):
        user = self.request.user
        email = form.cleaned_data['email']
        user.email = email
        user.save()
        try:
            user_profile = Profile.objects.get(user_id=user.id)
        except user_profile.DoesNotExist:
            user_profile = None
        date = form.cleaned_data['date_format']
        time = form.cleaned_data['time_format']
        new_date = dt.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
        format_time = new_date + ' ' + time
        my_date = dt.datetime.strptime(format_time, '%Y-%m-%d %H:%M %p')
        user_profile.date_time = my_date
        user_profile.gender = form.cleaned_data['gender']
        user_profile.timezone = form.cleaned_data['timezone']
        user_profile.save()
        return super(AccountSettings, self).form_valid(form)

def form_invalid(self, form):
    return super(AccountSettings, self).form_invalid(form)


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
