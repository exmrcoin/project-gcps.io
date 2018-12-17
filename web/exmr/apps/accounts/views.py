import pyotp

from django import forms
from django.views import View
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from apps.common.utils import send_mail
from django.forms import formset_factory
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.views.generic import CreateView, TemplateView, FormView, UpdateView

from apps.accounts.models import Profile, ProfileActivation, TwoFactorAccount, Address,\
                                 Feedback, KYC, KYCTerms
from apps.accounts.decorators import check_2fa
from apps.coins.utils import *
from apps.coins.models import Coin, Wallet, Transaction
from apps.common.utils import generate_key, JSONResponseMixin, get_pin
from apps.accounts.forms import SignUpForm, UpdateBasicProfileForm, PublicInfoForm, LoginSecurityForm,\
                                IPNSettingsForm, AddressForm, KYCForm



class SignUpView(JSONResponseMixin, CreateView):
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
        return self.render_to_json_response({'msg': _('Activation mail sent')})

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors)

    def send_activation_mail(self, profile):
        """
        send activation mail
        :param profile:
        :return:
        """
        profile_activation, created = ProfileActivation.objects.get_or_create(
            user=profile.user)
        if created or profile_activation.expired:
            profile_activation.activation_key = generate_key(64)
            profile_activation.expired = False
        profile_activation.save()
        profile_activation.send_activation_email(
            get_current_site(self.request))


class SignUpCompleteView(TemplateView):
    template_name = 'accounts/signup_complete.html'


@method_decorator(check_2fa, name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = Transaction.objects.filter(user=self.request.user)[:10]
        return context


@method_decorator(check_2fa, name='dispatch')
class AddressView(LoginRequiredMixin, CreateView):
    template_name = 'accounts/address-book.html'
    form_class = AddressForm
    success_url = reverse_lazy('accounts:add_new_address_complete')

    def get_context_data(self, **kwargs):
        context = super(AddressView, self).get_context_data(**kwargs)
        context['address'] = self.request.user.get_user_addresses.all()
        return context

    def form_valid(self, form, commit=True):
        self.object = form.save(commit=False)
        user = self.request.user
        try:
            user = User.objects.get(username=user)
            self.object.user = user
        except User.DoesNotExist:
            print("User not found")
        if commit:
            self.object.save()
        messages.add_message(self.request, messages.INFO,
                             'Address details have been stored successfully')
        return super(AddressView, self).form_valid(form)


class AddAddressCompleteView(TemplateView):
    template_name = 'common/message.html'


@method_decorator(check_2fa, name='dispatch')
class AccountSettings(LoginRequiredMixin, JSONResponseMixin, UpdateView):
    form_class = UpdateBasicProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')

    def get_object(self, queryset=None):
        user_profile, created = Profile.objects.get_or_create(
            user=self.request.user)
        return user_profile

    def get_initial(self):
        initial = super(AccountSettings, self).get_initial()
        user = get_object_or_404(User, username=self.request.user)
        user_profile, created = Profile.objects.get_or_create(user_id=user.id)
        self.object = user_profile
        initial['email'] = self.request.user.email
        initial['confirm_email'] = self.request.user.email
        if created and user_profile.timezone:
            initial['timezone'] = user_profile.timezone
        elif user_profile.timezone:
            initial['timezone'] = user_profile.timezone
        initial['date_format'] = user_profile.date_format
        initial['time_format'] = user_profile.time_format
        initial['merchant_id'] = user_profile.merchant_id
        initial['ref_url'] = self.request.scheme + "://" + \
            self.request.META['HTTP_HOST'] + "?ref=" + user_profile.merchant_id
        initial['gender'] = user_profile.gender
        return initial

    def get_context_data(self, **kwargs):
        context = super(AccountSettings, self).get_context_data(**kwargs)
        context['public_info_form'] = PublicInfoForm(instance=self.object)
        context['security_form'] = LoginSecurityForm(instance=self.object)
        context['ipn_form'] = IPNSettingsForm(instance=self.object)
        context['ref_url'] = self.request.scheme + "://" + \
            self.request.META['HTTP_HOST'] + "?ref=" + self.object.merchant_id
        return context

    def form_invalid(self, form, *args, **kwargs):
        self.context = self.get_context_data(**kwargs)
        self.context.update({'form': form})
        return self.render_to_response(self.context)

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
        user_profile.date_format = date
        user_profile.time_format = time
        user_profile.gender = form.cleaned_data['gender']
        user_profile.timezone = form.cleaned_data['timezone']
        user_profile.save()
        messages.add_message(self.request, messages.SUCCESS, 'Information updated successfully')

        return super(AccountSettings, self).form_valid(form)
        


class PublicInfoSave(AccountSettings, UpdateView):

    form_class = PublicInfoForm

    def get_object(self, queryset=None):
        return self.request.user.get_profile

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Information updated successfully')
        return super(AccountSettings, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        self.context = self.get_context_data(**kwargs)
        self.context.update({'public_info_form': form})
        messages.add_message(self.request, messages.WARNING, form.errors)
        return self.render_to_response(self.context)


class SecurityInfoSave( AccountSettings, UpdateView):
    form_class = LoginSecurityForm

    def get_object(self, queryset=None):
        return self.request.user.get_profile

    def form_valid(self, form):
        response = dict()
        password = form.cleaned_data.pop('password')
        confirm_password = form.cleaned_data.pop('confirm_password')
        current_password = form.cleaned_data.pop('current_password')
        if password:
            if not self.request.user.check_password(current_password):
                response['msg'] = [_('Current password is incorrect')]
            if confirm_password != password:
                response['msg'] = [_("Passwords doesn't match")]
            else:
                self.request.user.set_password(password)
                self.request.user.save()
                response.update({'msg': _('Information updated successfully')})
        else:
            self.request.session['2fa_verified'] = True
            form.save()
            messages.add_message(self.request, messages.SUCCESS, 'Information updated successfully')
            response.update({'msg': _('Information updated successfully')})

        return super(AccountSettings, self).form_valid(form)

    def form_invalid(self, form, *args, **kwargs):
        self.context = super().get_context_data(**kwargs)
        self.context.update({'security_form': form})
        messages.add_message(self.request, messages.WARNING, form.errors)
        return self.render_to_response(self.context)


class IPNSettingsSave(LoginRequiredMixin, JSONResponseMixin, UpdateView):

    form_class = IPNSettingsForm

    def get_object(self, queryset=None):
        return self.request.user.get_profile

    def form_valid(self, form):

        response = dict()
        form.save()
        messages.add_message(self.request, messages.SUCCESS, 'Information updated successfully')
        response.update({'msg': _('Information updated successfully')})
        return self.render_to_json_response(response)

    def form_invalid(self, form, *args, **kwargs):
        self.context = super().get_context_data(**kwargs)
        self.context.update({'ipn_form': form})
        messages.add_message(self.request, messages.WARNING, form.errors)
        return self.render_to_response(self.context)


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
                context['status'] = _(
                    'Account activated <br><p>Please <a href=/login>login</a><p>')
        return context


@method_decorator(check_2fa, name='dispatch')
class TwoFactorAccountView(LoginRequiredMixin, CreateView):
    """
        creating new two factor authentication account for current user
    """
    model = TwoFactorAccount
    fields = ['account_name', 'totp']
    template_name = 'accounts/2fa_account.html'
    success_url = reverse_lazy('accounts:accounts_2fa')
    key = pyotp.random_base32()

    def get_context_data(self, **kwargs):
        context = super(TwoFactorAccountView, self).get_context_data(**kwargs)
        context['object_list'] = self.request.user.get_user_2fa.all()
        return context

    def form_valid(self, form):
        """
        modifying form data before validation

        """
        totp_code = self.request.POST.get('totp')
        totp = pyotp.TOTP(self.key)

        if totp.verify(totp_code):
            form.instance.user = self.request.user
            form.instance.key = self.key
            form.instance.account_type = 'google_authenticator'
            form.instance.totp = None
            self.key = pyotp.random_base32()

            return super().form_valid(form)
        else:
            form.add_error('totp', 'Invalid Authentication Code')
            return self.form_invalid(form)


@method_decorator(check_2fa, name='dispatch')
class DeleteTwoFactorAccount(LoginRequiredMixin, DeleteView):
    """
        removing 2fa account from active list
    """
    model = TwoFactorAccount
    success_url = reverse_lazy('accounts:accounts_2fa')
    template_name = 'accounts/2fa_confirm_delete.html'

@method_decorator(check_2fa, name='dispatch')
class DeleteAddress(LoginRequiredMixin, DeleteView):
    """
        removing 2fa account from active list
    """
    model = Address
    success_url = reverse_lazy('accounts:address')
    # template_name = 'accounts/2fa_confirm_delete.html'



@method_decorator(check_2fa, name='dispatch')
class TwoFactorAccountList(LoginRequiredMixin, ListView):
    """
        listing all active 2fa accounts
    """
    model = TwoFactorAccount
    template_name = 'accounts/2fa_account_list.html'


class Verify2FAView(LoginRequiredMixin, View):
    """ verifying 2fa password"""
    template_name = 'accounts/verify_2fa.html'
    def get(self, request, *args, **kwargs):
        if request.user.get_profile.two_factor_auth == 0 or \
                not TwoFactorAccount.objects.filter(account_type='google_authenticator').exists():
            two_factor_type = 'Email'
            request.session['email_otp'] = get_pin()
            if not request.session.get('email_send', False):
                context = {
                   "ip": self.get_client_ip(request),
                   "username": request.user.username,
                   "otp": request.session['email_otp'],
                   }
                msg_plain = render_to_string('common/2_fact_auth_code.txt', context)
                send_mail(
                    request.user,
                    'Verification Code',
                    msg_plain,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False
                )

                request.session['email_send'] = True

        elif request.user.get_profile.two_factor_auth == 2:
            two_factor_type = 'Google'

        return render(request, self.template_name, {'two_factor_type': two_factor_type})

    def post(self, request, *args, **kwargs):
        otp_code = self.request.POST.get('otp')

        if request.user.get_profile.two_factor_auth == 0 or \
                not TwoFactorAccount.objects.filter(account_type='google_authenticator').exists():
            two_factor_type = 'Email'

            if request.session.get('email_otp') == otp_code:
                request.session['2fa_verified'] = True
                return redirect(reverse('accounts:profile'))

        elif request.user.get_profile.two_factor_auth == 2:
            auth_accounts = TwoFactorAccount.objects.filter(
                account_type='google_authenticator')
            two_factor_type = 'Google'

            for auth_account in auth_accounts:
                totp = pyotp.TOTP(auth_account.key)

                if totp.verify(otp_code):
                    self.request.session['2fa_verified'] = True
                    return redirect(reverse('accounts:profile'))

        context = {
            'two_factor_type': two_factor_type,
            'error': 'Incorrect Verification Code'
        }

        return render(request, self.template_name, context)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class FeedbackListView(ListView):
    template_name = 'accounts/feedback.html'
    model = Feedback
    queryset = Feedback.objects.all()
    context_object_name = 'feedback'

    def get_context_data(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        context = super(FeedbackListView, self).get_context_data(**kwargs)
        if slug:
            self.user = get_object_or_404(User,id=slug)
            context['user'] = self.user
            return context


class VerifyLoginView(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponse(json.dumps({'success':True}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'success':False}), content_type="application/json")

def signup_context(request):
    return {'signup_form':SignUpForm()}

class LoginNoticeView(View):
    def get(self, request, *args, **kwargs):
        try:
            status = self.send_login_notice(request)
        except:
            pass
        return redirect(reverse("accounts:profile"))

    def send_login_notice(self, request):
        context = {
                   "ip": self.get_client_ip(request),
                   "first_name": request.user.first_name
                   }
        msg_plain = render_to_string('accounts/login_notice.txt', context)
        send_mail(
                    'Login Notice',
                    msg_plain,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False
                )
        return True

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class KYCView(FormView):
    template_name = "accounts/kyc.html"
    form_class = KYCForm
    success_url = reverse_lazy('public coin vote')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = KYC.objects.filter(approved=True)
        
        context["kyc_terms"] = KYCTerms.objects.filter(user=self.request.user, flag=True)
        return context

    def form_valid(self,form):
        temp_form = form.save(commit=False)
        temp_form.user_id = self.request.user.id
        temp_form.save()
        messages.add_message(self.request, messages.INFO,
                             'Added KYC successfully, wait for some time to get approvel.')
        return redirect(reverse_lazy("home"))

class KYCAcceptanceView(View):

    def get(self, *args, **kwargs):
        status = int(self.request.GET.get('status'))
        obj, created = KYCTerms.objects.get_or_create(user= self.request.user)
        obj.flag = status
        obj.save()
        if status:
            return HttpResponse(json.dumps({"status": True}))
        return HttpResponse(json.dumps({"status": False}))

 