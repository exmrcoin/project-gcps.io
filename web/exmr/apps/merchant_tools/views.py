import time
import hashlib
import random
import string
import json
from django_unixdatetimefield import UnixDateTimeField
from django.core import serializers
from django.utils import six
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, CreateView, View
from django.contrib.sites.models import Site
from apps.accounts.models import Profile
from apps.coins.models import Coin, WalletAddress
from apps.coins.utils import *
from apps.coins import coinlist
from apps.merchant_tools.forms import ButtonMakerForm, CryptoPaymentForm, URLMakerForm, POSQRForm, DonationButtonMakerForm
from apps.merchant_tools.models import (ButtonImage, ButtonMaker, CryptoPaymentRec, MercSidebarTopic, ButtonInvoice,
                                        URLMaker, POSQRMaker, MultiPayment, MercSidebarSubTopic)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils import timezone

from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Create your views here.


class ButtonMakerView(FormView):

    template_name = 'merchant_tools/buttonmaker.html'
    form_class = ButtonMakerForm

    def get_success_url(self):
        success_url = self.request.path_info

    def get_initial(self):
        initial = super(ButtonMakerView, self).get_initial()
        try:
            initial['merchant_id'] = Profile.objects.get(
                user=self.request.user).merchant_id
        except:
            pass
        initial['btn_image'] = 1
        return initial

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.save()
        context = super(ButtonMakerView, self).get_context_data()
        merchant_id = form.cleaned_data['merchant_id']
        item_name = form.cleaned_data['item_name']
        item_amount = form.cleaned_data['item_amount']
        item_number = form.cleaned_data['item_number']
        item_qty = form.cleaned_data['item_qty']
        buyer_qty_edit = str(form.cleaned_data['buyer_qty_edit']).lower()
        invoice_number = form.cleaned_data['invoice_number']
        tax_amount = form.cleaned_data['tax_amount']
        allow_shipping_cost = str(
            form.cleaned_data['allow_shipping_cost']).lower()
        shipping_cost = form.cleaned_data['shipping_cost']
        shipping_cost_add = form.cleaned_data['shipping_cost_add']
        success_url_link = form.cleaned_data['success_url_link']
        cancel_url_link = form.cleaned_data['cancel_url_link']
        ipn_url_link = form.cleaned_data['ipn_url_link']
        btn_image = form.cleaned_data['btn_image']
        allow_buyer_note = str(form.cleaned_data['allow_buyer_note']).lower()
        # domain =  Site.objects.get_current()
        domain = self.request.get_host()
        temp_html = ['<form action="https://'+domain+reverse('mtools:cryptopayV2') + '" method="POST" >',
                     '<input type="hidden" name="merchant_id" value="'+merchant_id +
                     '" maxlength="128" id="id_merchant_id" required />',
                     '<input type="hidden" name="item_name" value="'+item_name +
                     '" maxlength="128" id="id_item_name" required />',
                     '<input type="hidden" name="item_amount" value="'+str(item_amount) +
                     '" maxlength="128" id="id_item_amount" required />',
                     '<input type="hidden" name="item_number" value="'+item_number +
                     '" maxlength="128" id="id_item_number" required />',
                     '<input type="hidden" name="item_qty" value="'+str(item_qty) +
                     '" maxlength="128" id="id_item_qty" required />',
                     '<input type="hidden" name="buyer_qty_edit" value="' +  buyer_qty_edit+
                     '" id="id_buyer_qty_edit" />',
                     '<input type="hidden" name="invoice_number" value="'+invoice_number +
                     '" maxlength="128" id="id_invoice_number" required />',
                     '<input type="hidden" name="tax_amount" value="'+str(tax_amount) +
                     '" maxlength="128" id="id_tax_amount" required />',
                     '<input type="hidden" name="allow_shipping_cost" value="' +allow_shipping_cost+
                     '"id="id_allow_shipping_cost" />',
                     '<input type="hidden" name="shipping_cost" value="'+str(shipping_cost) +
                     '" maxlength="128" id="id_shipping_cost" required />',
                     '<input type="hidden" name="shipping_cost_add" value="'+str(shipping_cost_add) +
                     '" maxlength="128" id="id_shipping_cost_add" required />',
                     '<input type="hidden" name="success_url_link" value="'+str(success_url_link) +
                     '" maxlength="128" id="id_success_url_link" required />',
                     '<input type="hidden" name="cancel_url_link" value="'+str(cancel_url_link) +
                     '" maxlength="128" id="id_cancel_url_link" required />',
                     '<input type="hidden" name="ipn_url_link" value="'+str(ipn_url_link) +
                     '" maxlength="128" id="id_ipn_url_linl" required />',
                     '<input type="hidden" name="allow_buyer_note" value="' +allow_buyer_note+
                     '"id="id_allow_buyer_note" />',
                     '<input type="hidden" name="btn_image" value="1"id="id_btn_image" />',
                     '<input type="image" src="https://'+str(domain+(ButtonImage.objects.get(label=btn_image)).btn_img.url)+'" alt="Buy Now with GetCryptoPayments.org"></form>'
                     ]
        context['btn_code'] = temp_html
        return render(self.request, 'merchant_tools/buttonmaker.html', context)


class DonationButtonMakerView(FormView):

    template_name = 'merchant_tools/donationbuttonmaker.html'
    form_class = DonationButtonMakerForm

    def get_success_url(self):
        success_url = self.request.path_info

    def get_initial(self):
        initial = super(DonationButtonMakerView, self).get_initial()
        try:
            initial['merchant_id'] = Profile.objects.get(
                user=self.request.user).merchant_id
        except:
            pass
        initial['btn_image'] = 1
        return initial

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.save()
        context = super(DonationButtonMakerView, self).get_context_data()
        merchant_id = form.cleaned_data['merchant_id']
        donation_name = form.cleaned_data['donation_name']
        donation_amount = form.cleaned_data['donation_amount']
        item_number = form.cleaned_data['item_number']
        allow_donator_to_adjust_amount = str(form.cleaned_data['allow_donator_to_adjust_amount']).lower()
        invoice_number = form.cleaned_data['invoice_number']
        tax_amount = form.cleaned_data['tax_amount']
        collect_shipping_address = str(
            form.cleaned_data['collect_shipping_address']).lower()
        shipping_cost = form.cleaned_data['shipping_cost']
        success_url_link = form.cleaned_data['success_url_link']
        cancel_url_link = form.cleaned_data['cancel_url_link']
        ipn_url_link = form.cleaned_data['ipn_url_link']
        btn_image = form.cleaned_data['btn_image']
        allow_donor_note = str(form.cleaned_data['allow_donor_note']).lower()
        # domain =  Site.objects.get_current()
        domain = self.request.get_host()
        temp_html = ['<form action="https://'+domain+reverse('mtools:cryptopay') + '" method="POST" >',
                     '<input type="hidden" name="merchant_id" value="'+merchant_id +
                     '" maxlength="128" id="id_merchant_id" required />',
                     '<input type="hidden" name="item_name" value="'+donation_name +
                     '" maxlength="128" id="id_item_name" required />',
                     '<input type="hidden" name="item_amount" value="'+str(donation_amount) +
                     '" maxlength="128" id="id_item_amount" required />',
                     '<input type="hidden" name="item_number" value="'+item_number +
                     '" maxlength="128" id="id_item_number" required />',
                     '<input type="hidden" name="item_qty" value="'+str(1) +
                     '" maxlength="128" id="id_item_qty" required />',
                     '<input type="hidden" name="buyer_qty_edit" value="' +  allow_donator_to_adjust_amount+
                     '" id="id_buyer_qty_edit" />',
                     '<input type="hidden" name="invoice_number" value="'+invoice_number +
                     '" maxlength="128" id="id_invoice_number" required />',
                     '<input type="hidden" name="tax_amount" value="'+str(tax_amount) +
                     '" maxlength="128" id="id_tax_amount" required />',
                     '<input type="hidden" name="allow_shipping_cost" value="' +collect_shipping_address+
                     '"id="id_allow_shipping_cost" />',
                     '<input type="hidden" name="shipping_cost" value="'+str(shipping_cost) +
                     '" maxlength="128" id="id_shipping_cost" required />',
                     '<input type="hidden" name="shipping_cost_add" value="'+str(1) +
                     '" maxlength="128" id="id_shipping_cost_add" required />',
                     '<input type="hidden" name="success_url_link" value="'+str(success_url_link) +
                     '" maxlength="128" id="id_success_url_link" required />',
                     '<input type="hidden" name="cancel_url_link" value="'+str(cancel_url_link) +
                     '" maxlength="128" id="id_cancel_url_link" required />',
                     '<input type="hidden" name="ipn_url_link" value="'+str(ipn_url_link) +
                     '" maxlength="128" id="id_ipn_url_linl" required />',
                     '<input type="hidden" name="allow_buyer_note" value="' +allow_donor_note+
                     '"id="id_allow_buyer_note" />',
                     '<input type="hidden" name="btn_image" value="1"id="id_btn_image" />',
                     '<input type="image" src="https://'+str(domain+(ButtonImage.objects.get(label=btn_image)).btn_img.url)+ '" alt="Buy Now with GetCryptoPayments.org"></form>'
                     ]
        context['btn_code'] = temp_html
        return render(self.request, 'merchant_tools/donationbuttonmaker.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class CryptoPaymment(FormView):
    template_name = 'merchant_tools/payincryptobtnmaker.html'
    form_class = CryptoPaymentForm

    def get_success_url(self):
        success_url = self.request.path_info

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CryptoPaymment, self).dispatch(request, *args, **kwargs)
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        mydate = timezone.now()
        context = super(CryptoPaymment, self).get_context_data()
        context['unique_id'] = get_random_string(
            length=32) + str(int(time.mktime(mydate.timetuple())*1000))

        context['merchant_id'] = self.request.POST['merchant_id']
        context['item_name'] = self.request.POST['item_name']
        context['item_amount'] = self.request.POST['item_amount']
        context['item_number'] = self.request.POST['item_number']
        context['item_qty'] = self.request.POST['item_qty']
        context['buyer_qty_edit'] = str(
            self.request.POST['buyer_qty_edit']).lower()
        context['invoice_number'] = self.request.POST['invoice_number']
        context['tax_amount'] = self.request.POST['tax_amount']
        context['allow_shipping_cost'] = str(
            self.request.POST['allow_shipping_cost']).lower()
        context['shipping_cost'] = self.request.POST['shipping_cost']
        context['shipping_cost_add'] = self.request.POST['shipping_cost_add']
        context['success_url_link'] = self.request.POST['success_url_link']
        context['cancel_url_link'] = self.request.POST['cancel_url_link']
        context['ipn_url_link'] = self.request.POST['ipn_url_link']
        context['btn_image'] = self.request.POST['btn_image']
        context['allow_buyer_note'] = self.request.POST['allow_buyer_note']
        temp_id = context['merchant_id']

        tax_amount = self.request.POST['tax_amount']
        shipping_cost_add = self.request.POST['shipping_cost_add']
        shipping_cost = self.request.POST['shipping_cost']
        item_amount = self.request.POST['item_amount']
        item_qty = self.request.POST['item_qty']
        if float(shipping_cost_add) > 1:
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * float(item_qty))
        else:
            total_shipping = float(shipping_cost)
        
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        return render(request, 'merchant_tools/payincryptobtnmaker.html', context)



class ResumeCryptoPaymment(FormView):
    template_name = 'merchant_tools/payincrypto.html'
    form_class = CryptoPaymentForm

    def get_success_url(self):
        success_url = self.request.path_info

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ResumeCryptoPaymment, self).dispatch(request, *args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        u_id = self.request.POST['unique_id']

        try:
            temp_obj = CryptoPaymentRec.objects.filter(unique_id = u_id)
            for payobj in temp_obj:
                pass


        except Exception as e:
            raise e





class PaymentFormSubmitView(View):
    def post(self, request, *args, **kwargs):
        print(self.request.POST['selected_coin'])
        try:
            print(self.request.POST['selected_coin'])
            sel_coin = Coin.objects.get(code=self.request.POST['selected_coin'])
        except:
            sel_coin = EthereumToken.objects.get(contract_symbol=self.request.POST['selected_coin'])
        superuser = User.objects.get(is_superuser=True)
        try:
            crypto_address = create_wallet(superuser, sel_coin.code)
        except:
            crypto_address = create_wallet(superuser, sel_coin.contract_symbol)
        # crypto_address = '123'
        print(crypto_address)
        try:
            temp_obj = CryptoPaymentRec.objects.create(
                merchant_id=self.request.POST['merchant_id'],
                item_name=self.request.POST['item_name'],
                item_amount=self.request.POST['item_amount'],
                item_number=self.request.POST['item_number'],
                item_qty=self.request.POST['item_qty'],
                invoice_number=self.request.POST['invoice_number'],
                unique_id=self.request.POST['unique_id'],
                tax_amount=self.request.POST['tax_amount'],
                shipping_cost=self.request.POST['shipping_cost'],
                first_name=self.request.POST['first_name'],
                last_name=self.request.POST['last_name'],
                email_addr=self.request.POST['email_addr'],
                addr_l1=self.request.POST['addr_line_1'],
                addr_l2=self.request.POST['addr_line_2'],
                country=self.request.POST['country'],
                city=self.request.POST['city'],
                zipcode=self.request.POST['zipcode'],
                phone=self.request.POST['phone'],
                selected_coin=sel_coin,
                wallet_address=crypto_address,
                buyer_note=self.request.POST['buyer_notes']
            )
        except:
            temp_obj = CryptoPaymentRec.objects.create(
                merchant_id=self.request.POST['merchant_id'],
                item_name=self.request.POST['item_name'],
                item_amount=self.request.POST['item_amount'],
                item_number=self.request.POST['item_number'],
                item_qty=self.request.POST['item_qty'],
                invoice_number=self.request.POST['invoice_number'],
                unique_id=self.request.POST['unique_id'],
                tax_amount=self.request.POST['tax_amount'],
                shipping_cost=self.request.POST['shipping_cost'],
                first_name=self.request.POST['first_name'],
                last_name=self.request.POST['last_name'],
                email_addr=self.request.POST['email_addr'],
                addr_l1=self.request.POST['addr_line_1'],
                addr_l2=self.request.POST['addr_line_2'],
                country=self.request.POST['country'],
                city=self.request.POST['city'],
                zipcode=self.request.POST['zipcode'],
                phone=self.request.POST['phone'],
                selected_erc_token = sel_coin, 
                wallet_address=crypto_address,
                buyer_note=self.request.POST['buyer_notes']
            )


        temp_obj.save()
        context = {}
        merchant_id = self.request.POST['merchant_id']
        context['available_coins'] = Coin.objects.filter(active=True)
        context['merchant_name'] = Profile.objects.get(merchant_id=merchant_id)
        context['crypto_address'] = crypto_address
        context['unique_id'] = self.request.POST['unique_id']
        context['selected_coin'] = sel_coin
        item_amount = float(self.request.POST['item_amount'])
        item_qty = float(self.request.POST['item_qty'])
        context['amt_payable_usd'] = (item_amount * item_qty)
        return render(request, 'merchant_tools/postpayment.html', context)


class MercDocs(TemplateView):
    template_name = 'merchant_tools/merc-help.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['merc_sidebar_topic'] = MercSidebarTopic.objects.all()
        context['merc_sidebar_sub_topic'] = MercSidebarSubTopic.objects.all()
        return context

class HelpTemplateView(TemplateView):
    template_name = 'merchant_tools/help-template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['merc_sidebar_topic'] = MercSidebarTopic.objects.all()
        context['merc_sidebar_sub_topic'] = MercSidebarSubTopic.objects.all() 
        # context['legal_sidebar'] = LegalSidebar.objects.all() 
        if (MercSidebarSubTopic.objects.filter(slug=slug)).exists():
            context['details'] = MercSidebarSubTopic.objects.filter(slug=slug)
        # else:
        #     context['details'] = LegalSidebar.objects.filter(slug=slug)
        return context

class URLMakerView(FormView):

    template_name = 'merchant_tools/urlmaker.html'
    form_class = URLMakerForm

    def get_success_url(self):
        success_url = self.request.path_info

    def get_initial(self):
        initial = super().get_initial()
        initial['merchant_id'] = Profile.objects.get(
            user=self.request.user).merchant_id
        return initial

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        obj = form.save(commit=False)
        context = super(URLMakerView, self).get_context_data()
        merchant_id = form.cleaned_data['merchant_id']
        item_name = form.cleaned_data['item_name']
        item_amount = form.cleaned_data['item_amount']
        item_number = form.cleaned_data['item_number']
        item_qty = form.cleaned_data['item_qty']
        invoice_number = form.cleaned_data['invoice_number']
        tax_amount = form.cleaned_data['tax_amount']
        shipping_cost = form.cleaned_data['shipping_cost']
        ipn_url_link = form.cleaned_data['ipn_url_link']
        domain = self.request.get_host()

        mydate = timezone.now()
        context = super(URLMakerView, self).get_context_data()
        merchant = Profile.objects.get(merchant_id=merchant_id).user
        context['unique_id'] = account_activation_token.make_token(
            user=merchant)
        token = context['unique_id']
        html_url = domain + \
            reverse('mtools:urlmakerinvoice', kwargs={'token': token})
        context['html_url'] = html_url
        obj.URL_link = html_url
        obj.unique_id = token
        obj.save()
        return render(self.request, 'merchant_tools/urlmaker.html', context)


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """ Overriding default Password reset token generator for email confirmation"""

    def _make_hash_value(self, user, timestamp):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))


account_activation_token = AccountActivationTokenGenerator()


class URLMakerInvoiceView(TemplateView):
    template_name = 'merchant_tools/payincrypto.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        token = self.kwargs['token']
        temp_obj = URLMaker.objects.get(unique_id=token)
        context['unique_id'] = temp_obj.unique_id
        context['merchant_id'] = temp_obj.merchant_id
        context['item_name'] = temp_obj.item_name
        context['item_amount'] = temp_obj.item_amount
        context['item_number'] = temp_obj.item_number
        context['item_qty'] = temp_obj.item_qty
        context['item_total'] = int(temp_obj.item_qty) * int(temp_obj.item_amount)
        context['invoice_number'] = temp_obj.invoice_number
        context['tax_amount'] = temp_obj.tax_amount
        context['shipping_cost'] = temp_obj.shipping_cost
        context['payable'] = (int(temp_obj.item_qty) * int(temp_obj.item_amount))+ temp_obj.shipping_cost + temp_obj.tax_amount
        context['ipn_url_link'] = temp_obj.ipn_url_link
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_obj.merchant_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        return context


class POSQRMakerView(FormView):
    template_name = 'merchant_tools/posqrgenerator.html'
    form_class = POSQRForm

    def get_success_url(self):
        success_url = self.request.path_info

    def get_initial(self):
        initial = super().get_initial()
        initial['merchant_id'] = Profile.objects.get(
            user=self.request.user).merchant_id
        initial['unique_id'] = account_activation_token.make_token(
            user=self.request.user)
        return initial

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        obj = form.save(commit=False)
        context = super(POSQRMakerView, self).get_context_data()
        merchant_id = form.cleaned_data['merchant_id']
        item_desc = form.cleaned_data['item_desc']
        item_amount = form.cleaned_data['item_amount']
        invoice_number = form.cleaned_data['invoice_number']
        custom_field = form.cleaned_data['custom_field']
        unique_id = form.cleaned_data['unique_id']
        d = timezone.now()
        time_now = int(time.mktime(d.timetuple()))
        obj.time_limit = time_now + 4*60*60
        domain = self.request.get_host()
        mydate = timezone.now()
        maxtimer = int(time.mktime(mydate.timetuple())) + 4*60*60
        print(maxtimer)

        context = super(POSQRMakerView, self).get_context_data()
        merchant = Profile.objects.get(merchant_id=merchant_id).user
        token = unique_id
        html_url = domain+reverse('mtools:pospay', kwargs={'token': token})
        context['html_url'] = html_url
        obj.URL_link = html_url
        obj.unique_id = token
        obj.save()
        return render(self.request, 'merchant_tools/posqrgenerator.html', context)


class POSQRPayView(TemplateView):
    template_name = 'merchant_tools/poscoinselect.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        token = self.kwargs['token']
        temp_obj = POSQRMaker.objects.get(unique_id=token)
        context['pos_sale'] = temp_obj
        context['available_coins'] = Coin.objects.filter(active=True)
        context['unique_id'] = token
        check_prepaid = MultiPayment.objects.filter(paid_unique_id=token)
        total_paid = 0;
        if check_prepaid:
            total_paid = 0;
            for prepaid in check_prepaid:
                total_paid = float(prepaid.recieved_usd)
            print(total_paid)
        try:
            context['amt_remaining'] = float(temp_obj.item_amount) - float(total_paid)                                     
        except:
            context['amt_remaining'] = float(temp_obj.item_amount)
        attempted = 0
        try:
            for prepaid in check_prepaid:
                attempted = attempted + float(prepaid.attempted_usd) 
                context['attempted'] = attempted
        except:
            pass
        return context

    def post(self, request, *args, **kwargs):
        superuser = User.objects.get(is_superuser=True)
        request.session['unique_id'] = request.POST.get('unique_id')
        request.session['selected_coin'] = request.POST.get('selected_coin')
        request.session['payable_amt'] = request.POST.get('coin_amt')
        request.session['payable_amt_usd'] = request.POST.get('payable_amt')
        d = timezone.now()
        try:
            try:
                obj = MultiPayment.objects.filter(paid_unique_id=request.session['unique_id'], paid_in=Coin.objects.get(
                    code=request.session['selected_coin']))
                addr = obj[0].payment_address
            except:
                obj = MultiPayment.objects.filter(paid_unique_id=request.session['unique_id'], paid_in_erc=EthereumToken.objects.get(
                    contract_symbol=request.session['selected_coin']))
                addr = obj[0].payment_address

        except:
            addr = create_wallet(
                superuser, self.request.session['selected_coin'])
        request.session['crypto_address'] = addr
        try:
            obj, created = MultiPayment.objects.get_or_create(
                paid_amount=request.session['payable_amt'],
                paid_in=Coin.objects.get(code=request.session['selected_coin']),
                eq_usd=request.session['payable_amt_usd'],
                paid_unique_id=request.session['unique_id'],
                attempted_usd = request.session['payable_amt_usd'],
                transaction_id=account_activation_token.make_token(
                    user=self.request.user),
                payment_address=addr
            )
        except:
            obj, created = MultiPayment.objects.get_or_create(
                paid_amount=request.session['payable_amt'],
                paid_in_erc=EthereumToken.objects.get(contract_symbol=request.session['selected_coin']),
                eq_usd=request.session['payable_amt_usd'],
                paid_unique_id=request.session['unique_id'],
                attempted_usd = request.session['payable_amt_usd'],
                transaction_id=account_activation_token.make_token(
                    user=self.request.user),
                payment_address=addr
            )


        return HttpResponseRedirect(reverse_lazy('mtools:posqrpay'))
        # return render(self.request, 'merchant_tools/posqrgenerator.html', context)


class POSQRCompletePaymentView(TemplateView):
    template_name = 'merchant_tools/posqrpostpayment.html'

    def get_context_data(self, *args, **kwargs):
        context = super(POSQRCompletePaymentView, self).get_context_data()
        unique_id = self.request.session['unique_id']
        obj = POSQRMaker.objects.get(unique_id=unique_id)
        time_limit = int(obj.time_limit)
        context['time_limit'] = time_limit
        context['unique_id'] = unique_id
        context['payable_amt'] = self.request.session['payable_amt']
        context['payable_amt_usd'] = self.request.session['payable_amt_usd']
        context['selected_coin'] = self.request.session['selected_coin']
        context['crypto_address'] = self.request.session['crypto_address']
        return context




class ButtonMakerContinuePayment(View):
    def post(self, request, *args, **kwargs):
        unique_id = self.request.POST.get('u_id')
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


@method_decorator(csrf_exempt, name='dispatch')
class CryptoPaymmentV2(FormView):
    template_name = 'merchant_tools/payincryptobtnmaker.html'
    form_class = CryptoPaymentForm

    def get_success_url(self):
        success_url = self.request.path_info

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CryptoPaymmentV2, self).dispatch(request, *args, **kwargs)
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        mydate = timezone.now()
        context = super(CryptoPaymmentV2, self).get_context_data()
        
        #unique_id is now deprecated
        context['unique_id'] = get_random_string(
            length=32) + str(int(time.mktime(mydate.timetuple())*1000))

        context['merchant_id'] = self.request.POST['merchant_id']
        context['item_name'] = self.request.POST['item_name']
        context['item_amount'] = self.request.POST['item_amount']
        context['item_number'] = self.request.POST['item_number']
        context['item_qty'] = self.request.POST['item_qty']
        context['buyer_qty_edit'] = str(
            self.request.POST['buyer_qty_edit']).lower()
        context['invoice_number'] = self.request.POST['invoice_number']
        context['tax_amount'] = self.request.POST['tax_amount']
        context['allow_shipping_cost'] = str(
            self.request.POST['allow_shipping_cost']).lower()
        context['shipping_cost'] = self.request.POST['shipping_cost']
        context['shipping_cost_add'] = self.request.POST['shipping_cost_add']
        context['success_url_link'] = self.request.POST['success_url_link']
        context['cancel_url_link'] = self.request.POST['cancel_url_link']
        context['ipn_url_link'] = self.request.POST['ipn_url_link']
        context['btn_image'] = self.request.POST['btn_image']
        context['allow_buyer_note'] = self.request.POST['allow_buyer_note']
        temp_id = context['merchant_id']

        tax_amount = self.request.POST['tax_amount']
        shipping_cost_add = self.request.POST['shipping_cost_add']
        shipping_cost = self.request.POST['shipping_cost']
        item_amount = self.request.POST['item_amount']
        item_qty = self.request.POST['item_qty']
        if float(shipping_cost_add) > 1:
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * float(item_qty))
        else:
            total_shipping = float(shipping_cost)
        
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        return render(request, 'merchant_tools/payincryptobtnmaker.html', context)

#revised button maker
class ButtonMakerInvoice(TemplateView):
    template_name = 'merchant_tools/btncoinselect.html'


    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            self.invoice_url = self.kwargs['token']
        except:
            self.invoice_url = False
        return super(ButtonMakerInvoice, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        domain = self.request.get_host()
        context = super().get_context_data()
        if self.invoice_url:
            temp_obj = ButtonInvoice.objects.get(URL_link__icontains = self.invoice_url)
            #
            shipping_cost_add = 0
            #
            temp_id = temp_obj.merchant_id
            tax_amount = temp_obj.tax_amount
            unique_id = temp_obj.unique_id
            
            # shipping_cost_add = self.request.POST['shipping_cost_add']
            shipping_cost = temp_obj.shipping_cost
            item_amount = temp_obj.item_amount
            item_qty = temp_obj.item_qty
            if float(shipping_cost_add) > 1:
                total_shipping = float(shipping_cost) + (float(shipping_cost_add) * float(item_qty))
            else:
                total_shipping = float(shipping_cost)
            
            context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
            context['item_total'] = round((float(item_qty) * float(item_amount)),2)
            context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
            context['available_coins'] = coinlist.payment_gateway_coins()

            #attempt payment
            check_prepaid = MultiPayment.objects.filter(paid_unique_id=unique_id)
            total_paid = 0;
            if check_prepaid:
                total_paid = 0;
                for prepaid in check_prepaid:
                    total_paid = float(prepaid.recieved_usd)
                print(total_paid)
            try:
                context['amt_remaining'] = float(temp_obj.item_amount) - float(total_paid)                                     
            except:
                context['amt_remaining'] = float(temp_obj.item_amount)
            attempted = 0
            try:
                for prepaid in check_prepaid:
                    attempted = attempted + float(prepaid.attempted_usd) 
                    
            except:
                pass
            context['attempted'] = attempted
            #attempt payment

            context['url'] = temp_obj.URL_link

            context['unique_id'] = temp_obj.unique_id
            context['available_coins'] = coinlist.payment_gateway_coins()
            return context


    def post(self, request, *args, **kwargs):
        context = super().get_context_data()
        mydate = timezone.now()
        token = account_activation_token.make_token(
            user=self.request.user)
        
        domain = self.request.get_host()
        html_url = domain + \
            reverse('mtools:btnpay2', kwargs={'token': token})
        if not self.invoice_url:
            try:
                temp_obj, created = ButtonInvoice.objects.get_or_create(
                    merchant_id = self.request.POST['merchant_id'],
                    unique_id = self.request.POST['unique_id'],
                    invoice_number = self.request.POST['invoice_number'],
                    item_name=self.request.POST['item_name'],
                    item_amount=self.request.POST['item_amount'],
                    item_number=self.request.POST['item_number'],
                    item_qty=self.request.POST['item_qty'],
                    tax_amount=self.request.POST['tax_amount'],
                    shipping_cost=self.request.POST['shipping_cost'],
                    first_name=self.request.POST['first_name'],
                    last_name=self.request.POST['last_name'],
                    email_addr=self.request.POST['email_addr'],
                    addr_l1=self.request.POST['addr_line_1'],
                    addr_l2=self.request.POST['addr_line_2'],
                    country=self.request.POST['country'],
                    city=self.request.POST['city'],
                    zipcode=self.request.POST['zipcode'],
                    phone=self.request.POST['phone'],
                    buyer_note=self.request.POST['buyer_notes'],
                    URL_link = html_url
                )
                if created:
                    temp_obj.save()  
            except:
                temp_obj = ButtonInvoice.objects.get(unique_id = self.request.POST['unique_id'])  
        else:
            try:
                self.invoice_url = domain + reverse('mtools:btnpay2', kwargs={'token': self.invoice_url})
                temp_obj = ButtonInvoice.objects.get(URL_link = self.invoice_url)
            except:
                pass
        #
        shipping_cost_add = 0
        #
        temp_id = temp_obj.merchant_id
        tax_amount = temp_obj.tax_amount
        unique_id = temp_obj.unique_id
        shipping_cost_add = self.request.POST['shipping_cost_add']
        shipping_cost = temp_obj.shipping_cost
        item_amount = temp_obj.item_amount
        item_qty = temp_obj.item_qty
        if float(shipping_cost_add) > 1:
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * float(item_qty))
        else:
            total_shipping = float(shipping_cost)
        
        context['unique_id'] = unique_id
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        print("testing uniqueness" + ','+ unique_id)
        #attempt payment
        check_prepaid = MultiPayment.objects.filter(paid_unique_id=unique_id)
        total_paid = 0;
        if check_prepaid:
            total_paid = 0;
            for prepaid in check_prepaid:
                total_paid = float(prepaid.recieved_usd)
            print(total_paid)
        try:
            context['amt_remaining'] = float(temp_obj.item_amount) - float(total_paid)                                     
        except:
            context['amt_remaining'] = float(temp_obj.item_amount)
        attempted = 0
        try:
            for prepaid in check_prepaid:
                attempted = attempted + float(prepaid.attempted_usd) 
                
        except:
            pass
        context['attempted'] = attempted
        #attempt payment

        context['url'] = temp_obj.URL_link

        context['available_coins'] = coinlist.payment_gateway_coins()
        return self.render_to_response(context)

class ButtonMakerPayView(TemplateView):
    template_name = 'merchant_tools/btnqrgenerator.html'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data()
        superuser = User.objects.get(is_superuser=True)
        unique_id = request.POST.get('unique_id')
        selected_coin = request.POST.get('selected_coin')
        payable_amt = request.POST.get('coin_amt')
        payable_amt_usd = request.POST.get('payable_amt')
        
        print( unique_id + ','+ selected_coin + ','+payable_amt + ','+payable_amt_usd)
        try:
            try:
                obj = MultiPayment.objects.filter(paid_unique_id=unique_id, paid_in=Coin.objects.get(
                    code=selected_coin))
                addr = obj[0].payment_address
            except:
                obj = MultiPayment.objects.filter(paid_unique_id=unique_id, paid_in_erc=EthereumToken.objects.get(
                    contract_symbol=selected_coin))
                addr = obj[0].payment_address

        except:
            addr = create_wallet(superuser, selected_coin)
        request.session['crypto_address'] = addr
        try:
            obj, created = MultiPayment.objects.get_or_create(
                paid_amount=payable_amt,
                paid_in=Coin.objects.get(code=selected_coin),
                eq_usd=payable_amt_usd,
                paid_unique_id=unique_id,
                attempted_usd = payable_amt_usd,
                transaction_id=account_activation_token.make_token(
                    user=self.request.user),
                payment_address=addr
            )
        except:
            obj, created = MultiPayment.objects.get_or_create(
                paid_amount=request.session['payable_amt'],
                paid_in_erc=EthereumToken.objects.get(contract_symbol=selected_coin),
                eq_usd=request.session['payable_amt_usd'],
                paid_unique_id=request.session['unique_id'],
                attempted_usd = request.session['payable_amt_usd'],
                transaction_id=account_activation_token.make_token(
                    user=self.request.user),
                payment_address=addr
            )

        # context['time_limit'] = time_limit
        context['unique_id'] = unique_id
        context['payable_amt'] = payable_amt
        context['payable_amt_usd'] = payable_amt_usd
        context['selected_coin'] = selected_coin
        context['crypto_address'] = addr

        return render(request, 'merchant_tools/btnqrgenerator.html', context)
