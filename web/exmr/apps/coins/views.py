from django.urls import reverse_lazy
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.views.generic import ListView, FormView, TemplateView, View

from apps.coins.utils import *
from apps.accounts.models import User
from apps.coins.forms import ConvertRequestForm
from apps.coins.models import Coin, CRYPTO, TYPE_CHOICES, CoinConvertRequest
from django.shortcuts import render

CURRENCIES = ['BTC','LTC', 'BCH', 'XRP']

class WalletsView(LoginRequiredMixin, TemplateView):
    template_name = 'coins/wallets.html'

    def get_context_data(self, *args, **kwargs):
        context = super(WalletsView, self).get_context_data(**kwargs)
        # for currency in CURRENCIES:
        #     coin = Coin.objects.get(code=currency)
        #     if not Wallet.objects.filter(user=self.request.user, name=coin):
        #         create_wallet(self.request.user, currency)
        context['wallets'] = Coin.objects.all()
        return context


class SupportedCoinView(ListView):

    template_name = 'coins/supported-coins.html'
    queryset = Coin.objects.filter(active=True)
    context_object_name = 'coins'

    def get_queryset(self, *args, **kwargs):
        type_dict = dict(TYPE_CHOICES)
        self.coin_type = dict(zip(type_dict.values(),type_dict.keys())).get(self.kwargs['type'],0)
        return self.queryset.filter(type=self.coin_type, active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SupportedCoinView, self).get_context_data(
            object_list=None, **kwargs)
        context['coin_types'] = TYPE_CHOICES
        context['selected_coin_type'] = self.coin_type
        return context


class ConvertCoinsView(FormView):

    template_name = 'coins/coin_conversion.html'
    form_class = ConvertRequestForm
    success_url = reverse_lazy('coins:conversion_final')

    def get_initial(self, **kwargs):
        initial = super(ConvertCoinsView, self).get_initial(**kwargs)
        if self.kwargs.get('from'):
            self.from_coin = get_object_or_404(
                Coin, code=self.kwargs.get('from'))
        if self.kwargs.get('to'):
            self.to_coin = get_object_or_404(Coin, code=self.kwargs.get('to'))

        # initial['wallet_from'] = self.from_coin
        # initial['wallet_to'] = self.to_coin
        return initial

    def get_context_data(self, **kwargs):
        context = super(ConvertCoinsView, self).get_context_data(**kwargs)
        context['coin_from'] = self.from_coin
        context['coin_to'] = self.to_coin
        context['wallet_from'] = self.from_coin
        context['wallet_to'] = self.to_coin
        return context

    def form_valid(self, form):
        # TODO validate the wallet addresses
        # TODO initiate coin conversion
        # TODO send email saying that conversion request is initiated
        coin_request = form.save(commit=False)
        coin_request.convert_from = self.from_coin
        coin_request.convert_to = self.to_coin
        coin_request.save()
        self.request.session['coin_request_id'] = coin_request.id
        return super(ConvertCoinsView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super(ConvertCoinsView, self).form_invalid(form)


class CoinConversionFinalView(TemplateView):
    """
    View that renders after coin conversion request is submitted
    Initiates conversion request
    Send mail

    """
    template_name = 'coins/coin_conversion_final.html'

    def get_context_data(self, **kwargs):
        context = super(CoinConversionFinalView,
                        self).get_context_data(**kwargs)
        coin_request_id = self.request.session.get('coin_request_id')
        context['coin_request'] = get_object_or_404(
            CoinConvertRequest, id=coin_request_id)

        if self.request.session.get('coin_request_id'):
            del self.request.session['coin_request_id']
        return context


class NewCoinAddr(TemplateView):
    template_name = 'coins/deposit.html'

    def get_context_data(self, **kwargs):
        context = super(NewCoinAddr, self).get_context_data(**kwargs)
        code = kwargs.get('currency')
        context['wallets']=Wallet.objects.get(user=self.request.user,  name__code=code).addresses.all()
        context['code'] = code
        return context

    def post(self, request, *args, **kwargs):
        code = kwargs.get('currency')
        address = create_wallet(request.user, code)
        if address:
            return HttpResponse(json.dumps(address), content_type='application/json')

class AddNewCoin(FormView):
    template_name = 'coins/host-coin.html'
    form_class = ConvertRequestForm

class PublicCoinVote(TemplateView):
    template_name = 'coins/public-coin-vote.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PublicCoinVote, self).get_context_data(**kwargs)
        context['coins'] = Coin.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        count = request.POST.get('count')
        coin_id = request.POST.get('id')
        if count and coin_id:
            obj = Coin.objects.get(id=coin_id)
            obj.vote_count += int(count)
            obj.save()
            context = {
                'coins':Coin.objects.all(),
            }
            response_data = render_to_string('coins/vote.html', context, )
            return HttpResponse(json.dumps(response_data), content_type='application/json') 



class CoinSettings(TemplateView):
    template_name = 'coins/coin_settings.html'

class CoinWithdrawal(TemplateView):
    template_name = 'coins/coin-withdrawal.html'



