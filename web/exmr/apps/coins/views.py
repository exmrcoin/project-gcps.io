import random
import string
import datetime

from datetime import datetime
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.views.generic import ListView, FormView, TemplateView, DetailView, View

from apps.coins.utils import *
from apps.accounts.models import User
from apps.coins.forms import ConvertRequestForm, NewCoinForm
from apps.coins.models import Coin, CRYPTO, TYPE_CHOICES, CoinConvertRequest, Transaction,\
                              CoinVote, ClaimRefund, NewCoin, CoPromotion, CoPromotionURL, \
                              WalletAddress, EthereumToken, Phases
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
        context["erc_wallet"] = EthereumToken.objects.all()
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


class NewCoinAddr(LoginRequiredMixin, TemplateView):
    template_name = 'coins/deposit.html'

    def get_context_data(self, **kwargs):
        context = super(NewCoinAddr, self).get_context_data(**kwargs)
        code = kwargs.get('currency')
        erc = EthereumToken.objects.filter(contract_symbol=code)
        if not erc:
            try:
                context['wallets'] = Wallet.objects.get(user=self.request.user,  name__code=code).addresses.all()
            except:
                create_wallet(self.request.user, code)
                context['wallets']=Wallet.objects.get(user=self.request.user,  name__code=code).addresses.all()
        else:
            try:
                context['wallets'] = EthereumTokenWallet.objects.get(user=self.request.user,  name__contract_symbol=code).addresses.all()
            except:
                create_wallet(self.request.user, code)
                context['wallets']=EthereumTokenWallet.objects.get(user=self.request.user,  name__contract_symbol=code).addresses.all()
        context['code'] = code
        return context

    def post(self, request, *args, **kwargs):
        code = kwargs.get('currency')
        address = create_wallet(request.user, code)
        if address:
            date = str(WalletAddress.objects.get(address=address).date.strftime('%B %d, %Y, %I:%M %p'))
            return HttpResponse(json.dumps({'address':address,'date':date}), content_type='application/json')

class AddNewCoin(FormView):
    template_name = 'coins/host-coin.html'
    form_class = ConvertRequestForm

class PublicCoinVote(TemplateView):
    template_name = 'coins/public-coin-vote.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PublicCoinVote, self).get_context_data(**kwargs)
        context['coins'] = NewCoin.objects.filter(approved=True).order_by('-vote_count')
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

    def get_context_data(self, *args, **kwargs):
        currency = self.kwargs['code']
        erc = EthereumToken.objects.filter(contract_symbol=currency)
        context = super().get_context_data(**kwargs)
        if erc:
            context['coin'] = EthereumToken.objects.get(contract_symbol=currency)
        else:
            context['coin'] = Coin.objects.get(code=currency)
        return context



class SendView(LoginRequiredMixin, View):
    """
    For sending coins to given address
    """

    def post(self, request, *args, **kwargs):
        address = request.POST.get('to')
        currency = kwargs.get('slug')
        amount = Decimal(request.POST.get('amount'))
        erc = EthereumToken.objects.filter(contract_symbol=currency)
        if currency not in ('eth', 'xlm', 'xmr','XRPTest') and not erc:
            access = getattr(apps.coins.utils, 'create_' +
                             currency+'_connection')()
            valid = access.sendtoaddress(address, amount)
            balance = get_balance(request.user.username, currency)
            balance = balance - amount
        elif currency == 'XRPTest':
            obj = XRP(self.request.user)
            # valid = obj.send(address, str(amount))
            balance = obj.balance()
            code = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(12))
            trans_obj =Transaction.objects.create(user=self.request.user, currency=currency,
                                       balance=balance, amount=amount, transaction_to=address,
                                       activation_code=code)

            self.request.session['transaction'] = trans_obj.system_tx_id
            slug = trans_obj.system_tx_id+"-"+code
            context = {
                'slug_val': slug,
                'host': self.request.get_host(),
                'scheme': self.request.scheme,
                'transaction': trans_obj,
                'type': currency,
            }
            response_data = render_to_string('coins/transfer-confirmed-email.html', context, )
            email = EmailMessage('Getcryptopayments.org Withdrawal Confirmation', response_data, to=[self.request.user.email])
            email.send()

            return HttpResponse(json.dumps({"success": True}), content_type='application/json')
        elif erc:
            obj = EthereumTokens(self.request.user,currency)
            balance = obj.balance()
            code = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(12))
            trans_obj =Transaction.objects.create(user=self.request.user, currency=currency,
                                       balance=balance, amount=amount, transaction_to=address,
                                       activation_code=code)

            self.request.session['transaction'] = trans_obj.system_tx_id
            slug = trans_obj.system_tx_id+"-"+code
            context = {
                'slug_val': slug,
                'host': self.request.get_host(),
                'scheme': self.request.scheme,
                'transaction': trans_obj,
                'type': currency,
            }
            response_data = render_to_string('coins/transfer-confirmed-email.html', context, )
            email = EmailMessage('Getcryptopayments.org Withdrawal Confirmation', response_data, to=[self.request.user.email])
            email.send()
            return HttpResponse(json.dumps({"success": True}), content_type='application/json')

        return HttpResponse(json.dumps(valid), content_type='application/json')

class SendSuccessView(TemplateView):
    template_name = 'coins/send-money-success.html'


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction'] = self.request.session['transaction'] 
        return context

class SendConfirmView(TemplateView):
    template_name = 'coins/send-money-confirm.html'


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        tx_id = kwargs.get('slug').split('-')[0]
        token = kwargs.get('slug').split('-')[1]
        t_obj = Transaction.objects.filter(system_tx_id=tx_id, activation_code=token).first()
        if t_obj:
            erc = EthereumToken.objects.filter(contract_symbol=t_obj.currency)
            if t_obj.currency == 'XRPTest':
                obj = XRP(self.request.user)
                valid = obj.send(t_obj.transaction_to, str(t_obj.amount))
                balance = obj.balance()
                t_obj.approved=True
                t_obj.balance = balance
                t_obj.transaction_id=valid
                t_obj.save()
            elif erc:
                obj = EthereumTokens(self.request.user,t_obj.currency)
                valid = obj.send(t_obj.transaction_to, str(t_obj.amount))
                balance = obj.balance()
                t_obj.approved=True
                t_obj.balance = balance
                t_obj.transaction_id=valid
                t_obj.save()
            context['status'] = True
        else:
            context['status'] = False
        return context

class VoteDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'coins/vote_details.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        coin_code = kwargs.get('currency') 
        coin_obj = NewCoin.objects.get(code = coin_code)
        coin_votes = CoinVote.objects.filter(coin__code = coin_code)
        if coin_votes:
            context['total_coins'] = NewCoin.objects.filter(approved=True).count()
            context['position'] = [obj.id for obj in NewCoin.objects.filter(approved=True).order_by('-vote_count')].index(coin_obj.id)+1
            context['votes_share_completed'] = coin_votes.filter(type="share" ).count()
            context['votes_follow_completed'] = coin_votes.filter(type="follow" ).count()
            context['votes_share'] = [source['source'] for source in  coin_votes.filter(user=self.request.user, type="share" ).values('source')]
            context['votes_follow'] = [source['source'] for source in  coin_votes.filter(user=self.request.user, type="follow").values('source')]
        context['coin'] = coin_obj
        return context

    def post(self, request, *args, **kwargs):
        currency_code = kwargs.get('currency')
        vote_source = request.POST.get('source')
        vote_type = request.POST.get('type')
        coin = NewCoin.objects.get(code=currency_code)
        obj,created = CoinVote.objects.get_or_create(user=request.user,\
                      coin=coin,type=vote_type,source=vote_source)
        coin.vote_count += int(10)
        coin.save()

        return HttpResponse(json.dumps({"success": True}), content_type='application/json') 

class RefundClaimView(LoginRequiredMixin, TemplateView):
    template_name = 'coins/coin_refund_claim.html'
    msgs = []

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_id = kwargs.get('slug')
        transaction_obj = self.validate_transaction_id(transaction_id) 
        context['transaction_obj'] = transaction_obj
        context['msgs'] = self.msgs
        return context
    
    def validate_transaction_id(self, transaction_id:str):
        trasaction_obj = get_object_or_404(Transaction, system_tx_id=transaction_id)
        # check if the user is already made a claim request
        if ClaimRefund.objects.filter(transaction__system_tx_id=transaction_id).exists():
            self.msgs.append({'text':"Already Applied for refund", 'class':'alert-danger'})
        
        return trasaction_obj
    def post (self, *args, **kwargs):
        
        transaction_id = self.request.POST.get('transation_id', None)
        transaction_obj = self.validate_transaction_id(transaction_id)
        send_addr = self.request.POST.get('send_addr', None)

        obj = ClaimRefund()
        obj.transaction = transaction_obj
        obj.send_addr = send_addr
        obj.save()

        return HttpResponse(json.dumps({"success": True}), content_type='application/json') 

class NewCoinAddView(FormView):
    template_name = "coins/public_coin_add.html"
    form_class = NewCoinForm
    success_url = reverse_lazy('public coin vote')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super(NewCoinAddView, self).form_invalid(form)

class PayByNameView(LoginRequiredMixin, TemplateView):
    template_name = "coins/paybyname.html"

class PayByNamePayView(LoginRequiredMixin, TemplateView):
    template_name = "coins/paybyname-payment.html"


class CopromotionView(TemplateView):
    template_name = "coins/copromotion-form.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['coins'] = NewCoin.objects.filter(approved=True)
        return context

    def post(self, request, *args, **kwargs):
        coin = NewCoin.objects.filter(id = request.POST.get('coin_id'), approved=True)
        total = int(request.POST.get('total'))
        if coin and request.POST.get('urls1') and request.POST.get('urls2') and\
        request.POST.get('urls3'):
            copromo_obj = CoPromotion.objects.create(coin=coin.first())
            for i in range(1,total+1):
                if request.POST.get('urls'+str(i)):
                    obj = CoPromotionURL.objects.create(url = request.POST.get('urls'+str(i)))
                    copromo_obj.urls.add(obj)
            copromo_obj.save()
            messages.add_message(request, messages.INFO, 'Success')
            return redirect(reverse_lazy('coins:copromotion-form'))
        else:
            return redirect(reverse_lazy('coins:copromotion-form'))

class BalanceView(View):
    def get(self, request, *args, **kwargs):
        currency_code = self.request.GET.get('code')
        try:
            balance = get_balance(self.request.user, currency_code)
        except:
            balance = 0
        if not balance:
            balance = 0
        data = {'balance':str(balance),'code':currency_code}
        return HttpResponse(json.dumps(data), content_type="application/json")

class VoteWinners(TemplateView):
    template_name = 'coins/winners.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        phases = Phases.objects.filter(time_stop__lt = datetime.now())
        context['phases'] = phases
        temp_list =[]
        for phase in phases:
            for temp in NewCoin.objects.filter(phase = phase.id):
                if temp.vote_count >= 35000:
                    temp_list.append(temp)
        context['newcoins'] = temp_list
        return context
