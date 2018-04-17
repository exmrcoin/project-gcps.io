from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView, FormView, UpdateView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from apps.accounts.forms import SignUpForm, UpdateBasicProfileForm, PublicInfoForm, LoginSecurityForm, IPNSettingsForm, \
     AddressForm
from apps.accounts.models import Profile, ProfileActivation
from apps.common.utils import generate_key, JSONResponseMixin


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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'


class TransactionHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/payment-history.html'


class AddressView(LoginRequiredMixin, CreateView):
    template_name = 'accounts/address-book.html'
    form_class = AddressForm
    success_url = reverse_lazy('accounts:add_new_address_complete')

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

    # def form_invalid(self, form):
    #     print(form.errors)
    #     return super(AddressView, self).form_valid(form)


class AddAddressCompleteView(TemplateView):
    template_name = 'common/message.html'



class AccountSettings(LoginRequiredMixin, JSONResponseMixin, UpdateView):
    form_class = UpdateBasicProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')

    def get_object(self, queryset=None):
        user_profile, created = Profile.objects.get_or_create(user=self.request.user)
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
        initial['ref_url'] = self.request.scheme +"://"+ self.request.META['HTTP_HOST'] + "?ref="  + user_profile.merchant_id
        initial['gender'] = user_profile.gender
        return initial

    def get_context_data(self, **kwargs):
        context = super(AccountSettings, self).get_context_data(**kwargs)
        context['public_info_form'] = PublicInfoForm(instance=self.object)
        context['security_form'] = LoginSecurityForm(instance=self.object)
        context['ipn_form'] = IPNSettingsForm(instance=self.object)
        context['ref_url'] = self.request.scheme + "://" + self.request.META['HTTP_HOST'] + "?ref=" + self.object.merchant_id
        return context

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors)

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
        super(AccountSettings, self).form_valid(form)
        return self.render_to_json_response({'msg': _('Account details updated successfully')})


class PublicInfoSave(JSONResponseMixin, UpdateView):


    form_class = PublicInfoForm

    def get_object(self, queryset=None):
        return self.request.user.get_profile

    def form_valid(self, form):
        form.save()
        return self.render_to_json_response({'msg': _('Information updated successfully')})

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors)


class SecurityInfoSave(LoginRequiredMixin, JSONResponseMixin, UpdateView):

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
                response['current_password'] = [_('Current password is incorrect')]
            if confirm_password != password:
                response['password'] = [_("Passwords doesn't match")]
            else:
                self.request.user.set_password(password)
                self.request.user.save()
        else:
            form.save()
            response.update({'msg': _('Information updated successfully')})

        return self.render_to_json_response(response)

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors)


class IPNSettingsSave(LoginRequiredMixin, JSONResponseMixin, UpdateView):

    form_class = IPNSettingsForm

    def get_object(self, queryset=None):
        return self.request.user.get_profile

    def form_valid(self, form):

        response = dict()
        form.save()
        response.update({'msg': _('Information updated successfully')})
        return self.render_to_json_response(response)

    def form_invalid(self, form):
        return self.render_to_json_response(form.errors)


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
