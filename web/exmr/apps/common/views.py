import os
import itertools

from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View, TemplateView, FormView
from django.shortcuts import render
from apps.accounts.models import Profile
from apps.common.forms import CoinRequestForm, ContactForm
from apps.common.models import FAQ, AnnouncementHome, HelpSidebar, UITheme, LegalSidebar, PluginDownload, StaticPage, API, InformationalSidebar, ReceivingSidebar
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from apps.common.utils import send_mail
from apps.coins import coinlist
from django.core.mail import mail_admins
from django.conf import settings
from django.template.loader import render_to_string

class HomeView(TemplateView):
    template_name = 'gcps/test_base.html'

    def get_context_data(self, **kwargs):
        merchant_id = self.request.GET.get('ref')
        context = super(HomeView, self).get_context_data(**kwargs)
        # try:
        #     curr_theme = self.request.session['curr_theme']
        # except:
        #     curr_theme = ''
        #     self.request.session['curr_theme'] = 'Night'
        # theme
        announcements = AnnouncementHome.objects.all()
        if merchant_id:
            user_profile = Profile.objects.get(merchant_id=merchant_id)
            referance_count = user_profile.referance_count
            referance_count = referance_count + 1
            user_profile.referance_count = referance_count
            user_profile.save()
        d = coinlist.get_supported_coin()
        n = len(d) // 2          # length of smaller half
        i = iter(d.items())      # alternatively, i = d.iteritems() works in Python 2

        context['d1'] = dict(itertools.islice(i, n))   # grab first n items
        context['d2'] = dict(i)
        context['announce'] = announcements                        # grab the rest
        # context['theme'] = curr_theme
        # print(context['d1'])
        return context

def theme_context(request):
    try:
        theme = request.session['curr_theme']
    except:
        theme = 'Night'
    return {'theme': theme,}

class ModeChangeView(View):

    def post(self, request, *args, **kwargs):
        curr_theme = request.POST['theme']
        if curr_theme == 'Day':
            self.request.session['curr_theme'] = 'Night'
        else:
            self.request.session['curr_theme'] = 'Day'

        print(self.request.session['curr_theme'])
        return HttpResponse("test")

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
                    request.user,
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
            return HttpResponseRedirect(reverse_lazy('common:beta'))
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
    


class ApiView(TemplateView):
    template_name='common/inform-topic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api'] =  API.objects.all()
        context['inform_sidebar'] = InformationalSidebar.objects.all() 
        context['receive_sidebar'] = ReceivingSidebar.objects.all() 
        return context


class ApiTemplateView(TemplateView):
    template_name = 'common/inform-template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['inform_sidebar'] = InformationalSidebar.objects.all() 
        context['receive_sidebar'] = ReceivingSidebar.objects.all() 
        if (InformationalSidebar.objects.filter(slug=slug)).exists():
            context['details'] = InformationalSidebar.objects.filter(slug=slug)
        else:
            context['details1'] = ReceivingSidebar.objects.filter(slug=slug)
        return context

