import csv
import random
import string
import datetime
import requests
import paypalrestsdk
import apps.coins.utils

from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.views.generic import ListView, FormView, TemplateView, DetailView, View

from apps.coins.utils import *
from apps.coins import coinlist
from apps.apiapp import shapeshift
from apps.accounts.models import User, KYC
from apps.accounts.decorators import check_2fa
from apps.coins.forms import ConvertRequestForm, NewCoinForm
from apps.coins.models import Coin, CRYPTO, TYPE_CHOICES, CoinConvertRequest, Transaction,\
    CoinVote, ClaimRefund, NewCoin, CoPromotion, CoPromotionURL, PayByNamePackage, \
    WalletAddress, EthereumToken, Phases, ConvertTransaction, PaypalTransaction


paypalrestsdk.configure({
              "mode": settings.PAYPAL_MODE, # sandbox or live
              "client_id": settings.PAYPAL_CLIENT_ID,
              "client_secret": settings.PAYPAL_CLIENT_SECRET 
              })

@method_decorator(check_2fa, name='dispatch')
class WalletsView(LoginRequiredMixin, TemplateView):
    template_name = 'coins/wallets.html'

    def get_context_data(self, *args, **kwargs):
        context = super(WalletsView, self).get_context_data(**kwargs)
        # for currency in CURRENCIES:
        #     coin = Coin.objects.get(code=currency)
        #     if not Wallet.objects.filter(user=self.request.user, name=coin):
        #         create_wallet(self.request.user, currency)
        data = json.loads(requests.get("http://coincap.io/front").text)
        rates = {rate['short']:rate['price'] for rate in data}
        self.request.session["rates"] = rates
        context["wallets"] = Coin.objects.all()
        context["erc_wallet"] = EthereumToken.objects.all()
        context['transactions'] = Transaction.objects.filter(user=self.request.user)
        return context


class CoinConvertView(LoginRequiredMixin, TemplateView):
    template_name = 'coins/convert-select.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CoinConvertView, self).get_context_data(**kwargs)
        sel_coin = self.kwargs.get('currency')
        shapehift_available_coin = shapeshift.get_coins()
        image_path_list = {}
        exmr_list = coinlist.get_all_active_coin_code()
        available_coins = filter(lambda x: x in list(
            shapehift_available_coin), exmr_list)
        print(available_coins)
        for coin in list(shapehift_available_coin):
            for coin in exmr_list:
                if not coin == sel_coin:
                    try:
                        image_path_list[coin] = shapehift_available_coin[coin]['image']
                    except:
                        pass
                else:
                    try:
                        shapehift_available_coin.pop(coin, 0)
                    except:
                        pass

        context['coin_images'] = image_path_list
        context['avbl_coins'] = list(available_coins)
        context['sel_coin'] = sel_coin
        return context


class CoinConvertView2(LoginRequiredMixin, TemplateView):
    template_name = 'coins/convert-select.html'

    def post(self, request, *args, **kwargs):
        context = super(CoinConvertView2, self).get_context_data()
        sel_coin = request.POST.get('sel_coin')
        output_coin = request.POST.get('coin_radio')
        shapehift_available_coin = shapeshift.get_coins()
        for coin in list(shapehift_available_coin):
            if coin == output_coin:
                context['output_coin_img'] = shapehift_available_coin[coin]['image']
            elif coin == sel_coin:
                context['input_coin_img'] = shapehift_available_coin[coin]['image']
        context['input_coin'] = sel_coin
        context['output_coin'] = output_coin
        pair = None
        context['has_balance'] = True
        try:
            limit_json = shapeshift.get_market_info(sel_coin, output_coin)
            try:
                cur_bal = get_balance(self.request.user, sel_coin)
                if cur_bal < (limit_json['minimum'] * 1.3):
                    context['has_balance'] = False
                    
            except:
                pass
            pair = limit_json['pair']
            context['rate_json'] = limit_json['rate']
            context['min_limit'] = round(1.3 * limit_json['minimum'], 8)
            context['max_limit'] = round(0.75 * limit_json['limit'], 8)
            print(limit_json['minimum'])
            print(limit_json['limit'])
            try:
                balance = get_balance(self.request.user, sel_coin)
            except:
                balance = 0
            if not balance:
                balance = 0
            context['balance'] = balance
            context['miner_fee'] = limit_json['minerFee']
        except:
            pass
        try:
            addr = get_primary_address(
                user=self.request.user, currency=output_coin)
            ret_addr = get_primary_address(
                user=self.request.user, currency=sel_coin)
            # ret_addr = 'LXA3i9eEAVDbgDqkThCa4D6BUJ3SEULkEr'
            transaction_details = shapeshift.create_normal_tx(
                addr, sel_coin, output_coin, ret_addr, None, None, None)
            print(transaction_details)
            try:
                request.session['deposit_address'] = transaction_details['deposit']
                request.session['recieve_from'] = transaction_details['withdrawal']
                request.session['input_coin'] = sel_coin

                obj = ConvertTransaction.objects.create(
                    user=self.request.user,
                    input_coin=sel_coin,
                    output_coin=output_coin,
                    transaction_id=transaction_details['orderId'],
                    address_from=ret_addr,
                    address_to=transaction_details['deposit'],
                    receive_address=transaction_details['withdrawal'],
                    status=False,
                )
                obj.save()
            except:
                return HttpResponseServerError()

        except Exception as e:
            raise e
        return render(request, 'coins/convert-select-confirm.html', context)


class CoinConvertView3(TemplateView):
    template_name = 'coins/convert-select-finished.html'

    def post(self, request, *args, **kwargs):
        context = super(CoinConvertView3, self).get_context_data()
        input_coin_value = request.POST.get('input_coin_value')
        try:
            convert_address = request.session['deposit_address']
            coin = request.session['input_coin']
        except:
            return HttpResponseServerError()
        valid = False
        balance = get_balance(request.user, coin)
        valid =getattr(apps.coins.utils,coin)(self.request.user, coin).send( convert_address, input_coin_value)

        # valid = {'error':'test error'}
        if valid:
            context['result'] = "Success. Your account will be credited with 12 Hours. If not please contact support."

            trans_obj = Transaction.objects.create(user=self.request.user, currency=coin,
                                               balance=balance, amount=input_coin_value, transaction_to=convert_address,
                                               activation_code='coin convert')
        else:
            context['result'] = "Transaction failed. "
            context['result1'] = "Retry after some time. If your account has been deducted please contact support."
            context['result2'] = " Message: insufficient funds for value and transaction charges"

        return render(request, 'coins/convert-select-finished.html', context)


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


class SupportedCoinView(ListView):

    template_name = 'coins/supported-coins.html'
    queryset = Coin.objects.filter(active=True)
    context_object_name = 'coins'
    
    def get_queryset(self, *args, **kwargs):
        
        type_dict = dict(TYPE_CHOICES)
        self.coin_type = dict(zip(type_dict.values(), type_dict.keys())).get(
            self.kwargs['type'], 0)
        return self.queryset.filter(type=self.coin_type, active=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SupportedCoinView, self).get_context_data(
            object_list=None, **kwargs)
        context['coin_types'] = TYPE_CHOICES
        context['selected_coin_type'] = self.coin_type
        context['active_coins'] = coinlist.get_supported_coin()
        context['tokens'] = EthereumToken.objects.filter(display=True)
        context["ripples"] = Coin.objects.filter(code__icontains='XRP')
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


class NewCoinAddr(LoginRequiredMixin, TemplateView):
    template_name = 'coins/deposit.html'
    
    def get_context_data(self, **kwargs):
        context = super(NewCoinAddr, self).get_context_data(**kwargs)
        code = kwargs.get('currency')
        erc = EthereumToken.objects.filter(contract_symbol=code)
        if not erc:
            try:
                context['wallets'] = Wallet.objects.get(
                    user=self.request.user,  name__code=code).addresses.all()
            except:
                create_wallet(self.request.user, code)
                context['wallets'] = Wallet.objects.get(
                    user=self.request.user,  name__code=code).addresses.all()
        else:
            try:
                context['wallets'] = EthereumTokenWallet.objects.get(
                    user=self.request.user,  name__contract_symbol=code).addresses.all()
            except:
                create_wallet(self.request.user, code)
                context['wallets'] = EthereumTokenWallet.objects.get(
                    user=self.request.user,  name__contract_symbol=code).addresses.all()
        context['code'] = code
        return context

    def post(self, request, *args, **kwargs):
        code = kwargs.get('currency')
        address = create_wallet(request.user, code)
        if address:
            date = str(WalletAddress.objects.get(
                address=address).date.strftime('%B %d, %Y, %I:%M %p'))
            return HttpResponse(json.dumps({'address': address, 'date': date}), content_type='application/json')


class AddNewCoin(FormView):
    template_name = 'coins/host-coin.html'
    form_class = ConvertRequestForm


class PublicCoinVote(TemplateView):
    template_name = 'coins/public-coin-vote.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PublicCoinVote, self).get_context_data(**kwargs)
        context['coins'] = NewCoin.objects.filter(
            approved=True).order_by('-vote_count')
        return context

    def post(self, request, *args, **kwargs):
        count = request.POST.get('count')
        coin_id = request.POST.get('id')
        if count and coin_id:
            obj = Coin.objects.get(id=coin_id)
            obj.vote_count += int(count)
            obj.save()
            context = {
                'coins': Coin.objects.all(),
            }
            response_data = render_to_string('coins/vote.html', context, )
            return HttpResponse(json.dumps(response_data), content_type='application/json')


class CoinSettings(TemplateView):
    template_name = 'coins/coin_settings.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CoinSettings, self).get_context_data(**kwargs)
        # for currency in CURRENCIES:
        #     coin = Coin.objects.get(code=currency)
        #     if not Wallet.objects.filter(user=self.request.user, name=coin):
        #         create_wallet(self.request.user, currency)
        data = json.loads(requests.get("http://coincap.io/front").text)
        rates = {rate['short']:rate['price'] for rate in data}
        self.request.session["rates"] = rates
        context["wallets"] = Coin.objects.all()
        context["erc_wallet"] = EthereumToken.objects.all()
        context['transactions'] = Transaction.objects.filter(user=self.request.user)
        return context

class SettingSetUp(TemplateView):
    template_name = 'coins/setting_setup.html'

class OMiniView(TemplateView):
    template_name = 'coins/omini.html'

class RippleView(TemplateView):
    template_name = 'coins/ripple.html'

    def get_context_data(self, *args, **kwargs):
        context = super(RippleView, self).get_context_data(**kwargs)
        # for currency in CURRENCIES:
        #     coin = Coin.objects.get(code=currency)
        #     if not Wallet.objects.filter(user=self.request.user, name=coin):
        #         create_wallet(self.request.user, currency)
        data = json.loads(requests.get("http://coincap.io/front").text)
        rates = {rate['short']:rate['price'] for rate in data}
        self.request.session["rates"] = rates
        context["ripple"] = Coin.objects.get(code='XRPTest')
        context["erc_wallet"] = EthereumToken.objects.all()
        context['transactions'] = Transaction.objects.filter(user=self.request.user)
        return context

class CoinWithdrawal(TemplateView):
    template_name = 'coins/coin-withdrawal.html'

    def get_context_data(self, *args, **kwargs):
        currency = self.kwargs['code']
        erc = EthereumToken.objects.filter(contract_symbol=currency)
        context = super().get_context_data(**kwargs)
        if erc:
            context['coin'] = EthereumToken.objects.get(
                contract_symbol=currency)
        else:
            context['coin'] = Coin.objects.get(code=currency)
        return context

@method_decorator(check_2fa, name='dispatch')
class SendView(LoginRequiredMixin, View):
    """
    For sending coins to given address
    """

    def post(self, request, *args, **kwargs):
        address = request.POST.get('to')
        currency = kwargs.get('slug')
        if '$' in address:
            if not PaybyName.objects.filter(label=address.strip('$')):
                return HttpResponse(json.dumps({"error": "Paybyname not found"}), content_type='application/json')
        amount = Decimal(request.POST.get('amount'))
        erc = EthereumToken.objects.filter(contract_symbol=currency)
        balance = get_balance(request.user, currency)
        if float(amount) > balance or amount<=0:
            return HttpResponse(json.dumps({"error": "Insufficient Funds"}), content_type='application/json')
    
        code = ''.join(random.choice(string.ascii_lowercase +
                                     string.ascii_uppercase) for _ in range(12))
        trans_obj = Transaction.objects.create(user=self.request.user, currency=currency,
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
        response_data = render_to_string(
            'coins/transfer-confirmed-email.html', context, )
        email = EmailMessage('Getcryptopayments.org Withdrawal Confirmation', response_data, to=[
                             self.request.user.email])
        email.send()
        return HttpResponse(json.dumps({"success": True}), content_type='application/json')


@method_decorator(check_2fa, name='dispatch')
class SendSuccessView(TemplateView):
    template_name = 'coins/send-money-success.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction'] = self.request.session['transaction']
        return context

@method_decorator(check_2fa, name='dispatch')
class SendConfirmView(TemplateView):
    template_name = 'coins/send-money-confirm.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        tx_id = kwargs.get('slug').split('-')[0]
        token = kwargs.get('slug').split('-')[1]
        t_obj = Transaction.objects.filter(
            system_tx_id=tx_id, activation_code=token).first()
        if t_obj:
            erc = EthereumToken.objects.filter(contract_symbol=t_obj.currency)
            if t_obj.currency == 'XRPTest':
                obj = XRPTest(self.request.user)
            elif t_obj.currency == 'XRP':
                obj = XRP(self.request.user)
            elif erc:
                obj = EthereumTokens(self.request.user, t_obj.currency)
            elif t_obj.currency == 'BTC':
                obj = BTC(self.request.user, t_obj.currency)
            elif t_obj.currency == 'ETH':
                obj = ETH(self.request.user, "ETH")
            elif t_obj.currency == 'XLM':
                obj = XLM(self.request.user, "XLM")
            elif t_obj.currency == 'XMR':
                obj = XMR(self.request.user, "XMR")
            valid = obj.send(t_obj.transaction_to, str(t_obj.amount))
            balance = obj.balance()
            t_obj.approved = True
            t_obj.balance = balance
            t_obj.transaction_id = valid
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
        coin_obj = NewCoin.objects.get(code=coin_code)
        coin_votes = CoinVote.objects.filter(coin__code=coin_code)
        if coin_votes:
            context['total_coins'] = NewCoin.objects.filter(
                approved=True).count()
            context['position'] = [obj.id for obj in NewCoin.objects.filter(
                approved=True).order_by('-vote_count')].index(coin_obj.id)+1
            context['votes_share_completed'] = coin_votes.filter(
                type="share").count()
            context['votes_follow_completed'] = coin_votes.filter(
                type="follow").count()
            context['votes_share'] = [source['source'] for source in coin_votes.filter(
                user=self.request.user, type="share").values('source')]
            context['votes_follow'] = [source['source'] for source in coin_votes.filter(
                user=self.request.user, type="follow").values('source')]
        context['coin'] = coin_obj
        return context

    def post(self, request, *args, **kwargs):
        currency_code = kwargs.get('currency')
        vote_source = request.POST.get('source')
        vote_type = request.POST.get('type')
        coin = NewCoin.objects.get(code=currency_code)
        obj, created = CoinVote.objects.get_or_create(user=request.user,
                                                      coin=coin, type=vote_type, source=vote_source)
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

    def validate_transaction_id(self, transaction_id: str):
        trasaction_obj = get_object_or_404(
            Transaction, system_tx_id=transaction_id)
        # check if the user is already made a claim request
        if ClaimRefund.objects.filter(transaction__system_tx_id=transaction_id).exists():
            self.msgs.append(
                {'text': "Already Applied for refund", 'class': 'alert-danger'})

        return trasaction_obj

    def post(self, *args, **kwargs):

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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paybynames"] = PaybyName.objects.filter(user = self.request.user)
        context["packages"] = PayByNamePackage.objects.all()
        return context


class PayByNamePayView(LoginRequiredMixin, DetailView):
    template_name = "coins/paybyname-payment.html"
    model = PayByNamePackage



class CopromotionView(TemplateView):
    template_name = "coins/copromotion-form.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['coins'] = NewCoin.objects.filter(approved=True)
        return context

    def post(self, request, *args, **kwargs):
        coin = NewCoin.objects.filter(
            id=request.POST.get('coin_id'), approved=True)
        total = int(request.POST.get('total'))
        if coin and request.POST.get('urls1') and request.POST.get('urls2') and\
                request.POST.get('urls3'):
            copromo_obj = CoPromotion.objects.create(coin=coin.first())
            for i in range(1, total+1):
                if request.POST.get('urls'+str(i)):
                    obj = CoPromotionURL.objects.create(
                        url=request.POST.get('urls'+str(i)))
                    copromo_obj.urls.add(obj)
            copromo_obj.save()
            messages.add_message(request, messages.INFO, 'Success')
            return redirect(reverse_lazy('coins:copromotion-form'))
        else:
            return redirect(reverse_lazy('coins:copromotion-form'))


class BalanceView(View):
    def get(self, request, *args, **kwargs):
        currency_code = self.request.GET.get('code')
        value = None
        if self.request.GET.get("user_id"):
            user = User.objects.get(id = self.request.GET.get("user_id"))
        else:
            user = request.user
        if not self.request.session.get("rates"):
            data = json.loads(requests.get("http://coincap.io/front").text)
            rates = {rate['short']:rate['price'] for rate in data}
            self.request.session["rates"] = rates
        if 'Test' in currency_code:
            new_currency_code = currency_code.strip("Test")
        else:
            new_currency_code = currency_code
        try:
            balance = get_balance(user, currency_code)
        except:
            balance = 0
        if not balance:
            balance = 0
        if self.request.session["rates"].get(new_currency_code):
            rate = self.request.session["rates"][new_currency_code]
            value = balance*rate
        else:
            value = "NA"
        data = {'balance': str(balance), 'code': currency_code, 'value': value}
        return HttpResponse(json.dumps(data), content_type="application/json")


class VoteWinners(TemplateView):
    template_name = 'coins/winners.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        phases = Phases.objects.filter(time_stop__lt=datetime.now())
        context['phases'] = phases
        temp_list = []
        for phase in phases:
            for temp in NewCoin.objects.filter(phase=phase.id):
                if temp.vote_count >= 35000:
                    temp_list.append(temp)
        context['newcoins'] = temp_list
        return context


class ConversionView(View):
    def get(self, request, *args, **kwargs):
        convert_to = self.request.GET.get("to")
        convert_from = self.request.GET.get("from")
        if not convert_from:
            convert_from = "USD"
        try:
            val = (float(requests.get("https://free.currencyconverterapi.com/api/v6/convert?q="+convert_from+"_"+\
            convert_to+"&compact=y&callback=json").text.split(":")[-1].strip("}});")))
        except:
            val = None
        self.request.session["coin_amount"] = val

        return HttpResponse(json.dumps({"value": val}), content_type="application/json")

class BuyCryptoView(TemplateView):
    template_name = "coins/buycrypto-1.html"
    
    @method_decorator(check_2fa)
    def dispatch(self, request, *args, **kwargs):
        kyc_status = KYC.objects.filter(user=self.request.user,approved=True)
        if not kyc_status:
            return redirect(reverse_lazy("accounts:kyc"))
        else:
            return super().get(request,**kwargs)

    def post(self, request, *args, **kwargs):
        context = {}
        coin_code = kwargs["currency"]
        coin_user = User.objects.get(is_superuser = True, username="admin")
        balance = get_balance(request.user, coin_code)
        amount = str(round(float(request.POST.get("usd_value")),4))
        currency = "USD"
        coin_amount = round(float(request.session["coin_amount"])*float(amount),4)
        if float(coin_amount) <= balance:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": "http://"+request.META['HTTP_HOST']+str(reverse_lazy("coins:paypal_verify")),
                    "cancel_url": "http://"+request.META['HTTP_HOST']},
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Coin",
                            "sku": coin_code,
                            "price": amount,
                            "currency": currency,
                            "quantity": 1}]},
                    "amount": {
                        "total": amount,
                        "currency": currency},
                    "description": coin_code+" buy transaction. Amount of "+amount+currency}]})

            if payment.create():
                PaypalTransaction.objects.create(
                    user = request.user,
                    amount = amount,
                    coin = Coin.objects.get(code = coin_code),
                    paypal_txid=payment.id,
                    coin_amount = coin_amount
                    )
                context["coin"] = coin_code
                context["coin_amount"] = coin_amount
                context["amount"] = amount
                context["payment_id"] = payment.id
                for link in payment.links:
                    if link.rel == "approval_url":
                        # Convert to str to avoid Google App Engine Unicode issue
                        # https://github.com/paypal/rest-api-sdk-python/pull/58
                        approval_url = str(link.href)
                        context["paypal_url"] = approval_url
            
                        return render(request,"coins/payment-gateway-selector.html", context=context)
        else:
            return redirect(reverse_lazy("coins:buy_coin",kwargs={'currency': coin_code})+"?error=true")
        

          
@method_decorator(check_2fa, name='dispatch')
class PayPalVerifyView(View):
    def get(self, request, *args, **kwargs):
        payment = paypalrestsdk.Payment.find(request.GET.get("paymentId"))

        if payment.execute({"payer_id": request.GET.get("PayerID")}):
            paypal_obj = PaypalTransaction.objects.get(user = request.user,
                        paypal_txid = request.GET.get("paymentId"))
            paypal_obj.tx_status=True
            self.send_coins(request, paypal_obj)
            paypal_obj.save()
            self.send_confirmation_mail(request, paypal_obj)
            status = True
            del request.session["coin_amount"]
        else:
            status = False
        return render(request,"coins/payment_status.html", context={"status": status})

    def send_confirmation_mail(self, request, paypal_obj):
        context = {
                   "ip": self.get_client_ip(request),
                   "first_name": request.user.first_name,
                   "coin_amount":paypal_obj.coin_amount,
                   "coin":paypal_obj.coin.code,
                   "amount":paypal_obj.amount
                   }
        msg_plain = render_to_string('coins/purchase_success.txt', context)
        send_mail(
                    'Purchase Confirmed',
                    msg_plain,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False
                )
        return True

    def send_coins(self, request, paypal_obj):
        coin_code = paypal_obj.coin.code
        coin_user = User.objects.get(is_superuser = True, username="admin")
        transaction_to = Wallet.objects.filter(user=self.request.user,
                         name__code=coin_code).first().addresses.all().first().address
        amount = paypal_obj.coin_amount
        erc = EthereumToken.objects.filter(contract_symbol=coin_code)
        if coin_code == 'XRPTest':
            obj = XRPTest(coin_user)
        elif coin_code == 'XRP':
            obj = XRP(coin_user)
        elif erc:
            obj = EthereumTokens(coin_user, coin_code)
        elif coin_code == 'BTC':
            obj = BTC(coin_user, coin_code)
        elif coin_code == 'ETH':
            obj = ETH(coin_user, "ETH")
        elif coin_code == 'XLM':
            obj = XLM(coin_user, "XLM")
        elif coin_code == 'XMR':
            obj = XMR(coin_user, "XMR")
        valid = obj.send(transaction_to, str(amount))
        balance = obj.balance()
        if type(valid) != dict:
            paypal_obj.system_tx_status = True

        trans_obj = Transaction.objects.create(user=self.request.user, currency=coin_code,
                                               balance=balance, amount=amount, transaction_to=transaction_to,
                                               activation_code="Buy Crypto")
        return True
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class DisplaySupportedCoins(View):
    def get(self, request, *args, **kwargs):
        currency_code = self.request.GET.get('code')
        coin_dict = coinlist.get_supported_coin()
        temp_list = list(coin_dict.keys())
        for coin in temp_list:
            if coin == currency_code:
                temp_list.remove(coin)
        print(temp_list)
        final_dict = { key: coin_dict[key] for key in temp_list }
        print(final_dict)
        data = final_dict
        return HttpResponse(json.dumps(data), content_type="application/json")

@method_decorator(check_2fa, name='dispatch')
class AdminWallet(TemplateView):
    template_name = "coins/system_stat.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_superuser:
            context["all_users"] = User.objects.filter(is_superuser=False)
            return context
        else:
            return context

@method_decorator(check_2fa, name='dispatch')
class UserWallet(TemplateView):
    template_name = "coins/system_stat.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["coins"] = Coin.objects.all()
        context["pk"] = kwargs["pk"]
        return context

@method_decorator(check_2fa, name='dispatch')
class TransactionHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'coins/payment-history.html'

    
@method_decorator(check_2fa, name='dispatch')
class TransactionDetails(LoginRequiredMixin, TemplateView):
    template_name = 'coins/transactions.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if kwargs["type"] == 'withdrawal':
            if self.request.GET.get('currency'):
                context["transactions"] = Transaction.objects.filter(user=self.request.user, currency=self.request.GET.get('currency'))
            else:
                context["transactions"] = Transaction.objects.filter(user=self.request.user)

        elif kwargs["type"] == 'deposit':
                if self.request.GET.get('currency'):
                    context["transactions"] = DepositTransaction(self.request.user).get_currency_txn(self.request.GET.get('currency'))
                else:
                    context["transactions"] = DepositTransaction(self.request.user).get_deposit_transactions()  
        return context

@method_decorator(check_2fa, name='dispatch')
class DownloadTxnView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        txns = reorder_tx_data(DepositTransaction(self.request.user).get_deposit_transactions())
        if request.GET.get('mode') == "export":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="export.csv"'

            writer = csv.writer(response)
            txns = reorder_tx_data(DepositTransaction(self.request.user).get_deposit_transactions())
            writer.writerow(['Time','Address', 'TX ID','Coin','Amount'])
            for txn in txns:
                writer.writerow(txn.values())

            return response
        else:
            response = render_to_string('coins/transaction_table.html',{'transactions': txns})
            return HttpResponse(json.dumps({'data': response}),content_type="application/json")
            
