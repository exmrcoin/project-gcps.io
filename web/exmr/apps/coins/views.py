from django.views.generic import ListView, FormView, TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.coins.forms import ConvertRequestForm
from apps.coins.models import Coin, CRYPTO, TYPE_CHOICES


class SupportedCoinView(ListView):

    template_name = 'coins/supported-coins.html'
    queryset = Coin.objects.filter(type=CRYPTO, active=True)
    context_object_name = 'coins'

    def get_queryset(self):
        print(type(self.request.GET.get('type', 0)))
        self.coin_type = int(self.request.GET.get('type', 0))
        return self.queryset.filter(type=self.coin_type, active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SupportedCoinView, self).get_context_data(object_list=None, **kwargs)
        context['coin_types'] = TYPE_CHOICES
        context['selected_coin_type'] = self.coin_type
        return context


class ConvertCoinsView(FormView):

    form_class = ConvertRequestForm()
    success_url = reverse_lazy('coins:conversion_final')

    def get_initial(self, **kwargs):
        initial = super(ConvertCoinsView, self).get_initial(**kwargs)
        if self.kwargs.get('from'):
            from_coin = get_object_or_404(Coin, code=self.kwargs.get('from'))
        if self.kwargs.get('to'):
            to_coin = get_object_or_404(Coin, code=self.kwargs.get('to'))

        initial['wallet_from'] = from_coin
        initial['wallet_to'] = to_coin
        return initial


class CoinConversionFinalView(TemplateView):
    """
    View that renders after coin conversion request is submitted
    Initiates conversion request
    Send mail

    """
    template_name = 'coins/coin_conversion_final.html'