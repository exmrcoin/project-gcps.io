import os

from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import View, TemplateView, FormView

from apps.accounts.models import Profile
from apps.common.forms import CoinRequestForm
from apps.common.models import FAQ, HelpSidebar, LegalSidebar, PluginDownload

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
            out = os.system("bash ~/webapps/update")
            return HttpResponse("Success "+str(out))
        except:
            return HttpResponse("Error")