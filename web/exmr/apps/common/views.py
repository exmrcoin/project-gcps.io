import os

from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View, TemplateView, FormView
from django.shortcuts import render
from apps.accounts.models import Profile
from apps.common.forms import CoinRequestForm, ContactForm
from apps.common.models import FAQ, HelpSidebar, LegalSidebar, PluginDownload, StaticPage
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.mail import send_mail
from django.core.mail import mail_admins
from django.conf import settings
from django.template.loader import render_to_string

class HomeView(TemplateView):
    template_name = 'common/index.html'

    def get_context_data(self, **kwargs):
        merchant_id = self.request.GET.get('ref')
        if merchant_id:
            user_profile = Profile.objects.get(merchant_id=merchant_id)
            referance_count = user_profile.referance_count
            referance_count = referance_count + 1
            user_profile.referance_count = referance_count
            user_profile.save()
        return super(HomeView, self).get_context_data(**kwargs)


class CoinRequestView(FormView):
    template_name = 'common/coin-hosting.html'
    form_class  = CoinRequestForm
    success_url = reverse_lazy('home')
 
    def form_valid(self,form):
        form.save()
        self.coin_request_notice(self.request)
        self.admin_coin_request_notice(self.request)
        return HttpResponseRedirect(self.success_url)

    def coin_request_notice(self, request):
        msg_plain = render_to_string('common/coin_request_email.txt')
        send_mail(
                    'Coin Request Notice',
                    msg_plain,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True
                )
        return True

    def admin_coin_request_notice(self, request):
        msg_plain = render_to_string('common/coin_request_email.txt')
        mail_admins(
                    'Coin Request Notice',
                    msg_plain,
                    fail_silently=False
                )
        return True

class HelpView(TemplateView):
    template_name='common/help-topic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faq'] =  FAQ.objects.all()
        context['help_sidebar'] = HelpSidebar.objects.all() 
        context['legal_sidebar'] = LegalSidebar.objects.all() 
        return context

class HelpTemplateView(TemplateView):
    template_name = 'common/help-template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['help_sidebar'] = HelpSidebar.objects.all() 
        context['legal_sidebar'] = LegalSidebar.objects.all() 
        if (HelpSidebar.objects.filter(slug=slug)).exists():
            context['details'] = HelpSidebar.objects.filter(slug=slug)
        else:
            context['details'] = LegalSidebar.objects.filter(slug=slug)
        return context

class PluginDownloadView(TemplateView):
    template_name = 'common/shopping-cart-plugin.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plugins'] = PluginDownload.objects.all()
        return context


class Update(View):
    def get(self, *args, **kwargs):
        try:
            os.system("bash ../../../update")
            return HttpResponse("Success ")
        except:
            return HttpResponse("Error")

class StaticPageView(TemplateView):
    template_name = 'common/staticpage.html'

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        context = self.get_context_data(**kwargs)
        try:
            if context['staticpage']:
                return handler(request, *args, **kwargs)
        except:
            return HttpResponseRedirect(reverse_lazy('common:beta'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        try:
            context['staticpage'] = StaticPage.objects.get(page_name=slug)
        except:
            pass
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class ContactView(FormView):
    template_name = 'common/contact.html'
    form_class  = ContactForm
    success_url = reverse_lazy('home')

    def form_valid(self,form):
        form.save()
        return HttpResponseRedirect(self.success_url)


