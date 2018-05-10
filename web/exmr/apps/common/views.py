from django.views.generic import TemplateView, FormView

from apps.accounts.models import Profile
from django.urls import reverse, reverse_lazy
from apps.common.forms import CoinRequestForm


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