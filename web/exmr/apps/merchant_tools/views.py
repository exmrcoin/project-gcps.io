import time
import hashlib
import random
import string
import json
import redis
import ast
import os

from datetime import timedelta, datetime
from django_unixdatetimefield import UnixDateTimeField
from django.core import serializers
from django.core.mail import EmailMessage
from django.utils import six
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, CreateView, View
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_control, never_cache
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT



from apps.accounts.models import Profile
from apps.coins.models import Coin, WalletAddress
from apps.coins.utils import *
from apps.coins import coinlist
from apps.merchant_tools.forms import ButtonMakerForm, CryptoPaymentForm, URLMakerForm, POSQRForm, DonationButtonMakerForm, SimpleButtonMakerForm
from apps.merchant_tools.models import (ButtonImage, ButtonMaker, CryptoPaymentRec, MercSidebarTopic, ButtonInvoice,
                                        URLMaker, POSQRMaker, MultiPayment, MercSidebarSubTopic, DonationButtonInvoice,ButtonItem, SimpleButtonItem, SimpleButtonInvoice)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils import timezone


from apps.apiapp.coingecko import CoinGeckoAPI

from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Create your views here.

eight_hours = datetime.datetime.now() - timedelta(hours=8)
coingecko = CoinGeckoAPI()
redis_object = redis.StrictRedis(host='localhost',
	port='6379',
	password='',
	db=0, charset="utf-8", decode_responses=True)

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
        item_uid = 'item_' + get_random_string(
            length=8) +'_' +str(int(time.mktime((timezone.now()).timetuple())))
        temp_item = ButtonItem.objects.get_or_create(
            item_unique_id = item_uid,
            item_name = item_name,
            item_amount = item_amount,
            merchant_id = merchant_id,
            shipping_cost = shipping_cost,
            shipping_cost_add = shipping_cost_add,
            item_tax = tax_amount
        )
        temp_html = ['<form action="https://'+domain+reverse('mtools:cryptopayV2') + '" method="POST" >',
                     '<input type="hidden" name="merchant_id" value="'+merchant_id +
                     '" maxlength="128" id="id_merchant_id" required />',
                     '<input type="hidden" name="item_name" value="'+item_name +
                     '" maxlength="128" id="id_item_name" required />',
                     '<input type="hidden" name="item_amount" value="'+str(item_amount) +
                     '" maxlength="128" id="id_item_amount" required />',
                     '<input type="hidden" name="item_number" value="'+item_number +
                     '" maxlength="128" id="id_item_number" required />',
                     '<input type="hidden" name="item_unique_id" value="'+item_uid +
                     '" maxlength="128" id="id_item_uid" required />',
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
                     '<input type="image" src="https://'+str(domain+(ButtonImage.objects.get(label=btn_image)).btn_img.url)+'"  alt="Buy Now with GetCryptoPayments.org" style="width: 200px;height: auto;"></form>'
                     ]
        context['btn_code'] = temp_html
        return render(self.request, 'merchant_tools/buttonmaker.html', context)

class SimpleButtonMakerView(FormView):

    template_name = 'merchant_tools/simplebuttonmaker.html'
    form_class = SimpleButtonMakerForm

    def get_success_url(self):
        success_url = self.request.path_info

    def get_initial(self):
        initial = super(SimpleButtonMakerView, self).get_initial()
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
        context = super(SimpleButtonMakerView, self).get_context_data()
        merchant_id = form.cleaned_data['merchant_id']
        item_name = form.cleaned_data['item_name']
        item_amount = form.cleaned_data['item_amount']
        item_number = form.cleaned_data['item_number']
        item_description = form.cleaned_data['item_description']
        # item_qty = form.cleaned_data['item_qty']
        # buyer_qty_edit = str(form.cleaned_data['buyer_qty_edit']).lower()
        invoice_number = form.cleaned_data['invoice_number']
        tax_amount = form.cleaned_data['tax_amount']
        allow_shipping_cost = str(
            form.cleaned_data['allow_shipping_cost']).lower()
        shipping_cost = form.cleaned_data['shipping_cost']
        # shipping_cost_add = form.cleaned_data['shipping_cost_add']
        success_url_link = form.cleaned_data['success_url_link']
        cancel_url_link = form.cleaned_data['cancel_url_link']
        ipn_url_link = form.cleaned_data['ipn_url_link']
        btn_image = form.cleaned_data['btn_image']
        # allow_buyer_note = str(form.cleaned_data['allow_buyer_note']).lower()
        # domain =  Site.objects.get_current()
        domain = self.request.get_host()
        item_uid = 'item_' + get_random_string(
            length=8) +'_' +str(int(time.mktime((timezone.now()).timetuple())))
        temp_item = SimpleButtonItem.objects.get_or_create(
            item_unique_id = item_uid,
            item_name = item_name,
            item_amount = item_amount,
            merchant_id = merchant_id,
            shipping_cost = shipping_cost,
            # shipping_cost_add = shipping_cost_add,
            item_tax = tax_amount
        )
        temp_html = ['<form action="https://'+domain+reverse('mtools:cryptopaysimple') + '" method="POST" >',
                     '<input type="hidden" name="merchant_id" value="'+merchant_id +
                     '" maxlength="128" id="id_merchant_id" required />',
                     '<input type="hidden" name="item_name" value="'+item_name +
                     '" maxlength="128" id="id_item_name" required />',
                     '<input type="hidden" name="item_amount" value="'+str(item_amount) +
                     '" maxlength="128" id="id_item_amount" required />',
                     '<input type="hidden" name="item_number" value="'+item_number +
                     '" maxlength="128" id="id_item_number" required />',
                     '<input type="hidden" name="item_unique_id" value="'+item_uid +
                     '" maxlength="128" id="id_item_uid" required />',
                     '<input type="hidden" name="item_qty" value="'+str(1) +
                     '" maxlength="128" id="id_item_qty" required />',
                     '<input type="hidden" name="buyer_qty_edit" value="' +  str(False)+
                     '" id="id_buyer_qty_edit" />',
                     '<input type="hidden" name="invoice_number" value="'+invoice_number +
                     '" maxlength="128" id="id_invoice_number" required />',
                     '<input type="hidden" name="tax_amount" value="'+str(tax_amount) +
                     '" maxlength="128" id="id_tax_amount" required />',
                     '<input type="hidden" name="allow_shipping_cost" value="' +allow_shipping_cost+
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
                     '<input type="hidden" name="allow_buyer_note" value="' +str(False)+
                     '"id="id_allow_buyer_note" />',
                     '<input type="hidden" name="btn_image" value="1"id="id_btn_image" />',
                     '<input type="image" src="https://'+str(domain+(ButtonImage.objects.get(label=btn_image)).btn_img.url)+'"  alt="Buy Now with GetCryptoPayments.org" style="width: 200px;height: auto;"></form>'
                     ]
        context['btn_code'] = temp_html
        return render(self.request, 'merchant_tools/simplebuttonmaker.html', context)

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
                     '<input type="image" src="https://'+str(domain+(ButtonImage.objects.get(label=btn_image)).btn_img.url)+ '"  alt="Buy Now with GetCryptoPayments.org" style="width: 200px;height: auto;"></form>'
                     ]
        context['btn_code'] = temp_html
        return render(self.request, 'merchant_tools/donationbuttonmaker.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class CryptoPaymment(FormView):
    template_name = 'merchant_tools/payincryptobtnmaker1.html'
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
        if ((float(shipping_cost_add)) > 0 and float(item_qty)>=1) :
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
        else:
            total_shipping = float(shipping_cost)
        
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        return render(request, 'merchant_tools/payincryptobtnmaker1.html', context)



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
        try:
            sel_coin = Coin.objects.get(code=self.request.POST['selected_coin'])
        except:
            sel_coin = EthereumToken.objects.get(contract_symbol=self.request.POST['selected_coin'])
        superuser = User.objects.get(is_superuser=True)
        try:
            crypto_address = create_wallet(superuser, sel_coin.code)
        except:
            crypto_address = create_wallet(superuser, sel_coin.contract_symbol)
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

class POSCalcView(TemplateView):
    template_name = 'gcps/merchant_tools/pos_calc.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data()
        return context


    def post(self, request, *args, **kwargs):
        input_amount =  request.POST.get('amountf')
        input_currency =  request.POST.get('select_currency')
        context = super().get_context_data(**kwargs)
        context['amount'] = input_amount
        context['input_currency'] = "usd"
        token = account_activation_token.make_token(
            user=self.request.user)
        domain = self.request.get_host()
        html_url = domain+reverse('mtools:poscalcpaysel', kwargs={'token': token})
        context['html_url'] = html_url
        context['available_coins'] = Coin.objects.filter(active=True)
        context['rates'] =  cache.get('rates')
        return render(self.request, 'gcps/merchant_tools/pos_coin_select.html', context)

class POSCalcPaySelView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_coins'] = Coin.objects.filter(active=True)
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
        self.request.session['merchant_id'] =  temp_obj.merchant_id
        context['pos_sale'] = temp_obj
        context['available_coins'] = Coin.objects.filter(active=True)
        context['unique_id'] = token
        check_prepaid = MultiPayment.objects.filter(paid_unique_id=token)
        total_paid = 0;
        if check_prepaid:
            total_paid = 0;
            for prepaid in check_prepaid:
                total_paid = float(prepaid.recieved_usd)
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
        merchant_id = self.request.session['merchant_id']
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
                merchant_id = merchant_id,
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
                merchant_id = merchant_id,
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
        final_dict = { key: coin_dict[key] for key in temp_list }
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
        context['item_unique_id'] = self.request.POST['item_unique_id']
        context['item_qty'] = self.request.POST['item_qty']
        context['buyer_qty_edit'] = str(
            self.request.POST['buyer_qty_edit']).lower()
        context['invoice_number'] = self.request.POST['invoice_number']
        context['allow_shipping_cost'] = str(
            self.request.POST['allow_shipping_cost']).lower()
        context['success_url_link'] = self.request.POST['success_url_link']
        context['cancel_url_link'] = self.request.POST['cancel_url_link']
        context['ipn_url_link'] = self.request.POST['ipn_url_link']
        context['btn_image'] = self.request.POST['btn_image']
        context['allow_buyer_note'] = self.request.POST['allow_buyer_note']
        item_code = self.request.POST['item_unique_id']
        temp_id = context['merchant_id']
        # 
        item_obj = ButtonItem.objects.get(item_unique_id = item_code)
        item_amount =  float(item_obj.item_amount)

        request.session['item_amount'] = item_amount
        shipping_cost_add = item_obj.shipping_cost_add
        shipping_cost = item_obj.shipping_cost
        item_amount =  float(item_obj.item_amount)
        tax_amount = float(item_obj.item_tax) * float(self.request.POST['item_qty'])
        context['tax_amount'] = tax_amount
        context['tax'] = float(item_obj.item_tax)
        item_qty = self.request.POST['item_qty']
        if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
        else:
            total_shipping = float(shipping_cost)
        context['shipping_add'] = float(shipping_cost_add)
        context['shipping'] = float(shipping_cost)
        context['shipping_cost'] = total_shipping
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        return render(request, 'merchant_tools/payincryptobtnmaker.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class CryptoPaymmentSimple(FormView):
    template_name = 'merchant_tools/payincryptobtnmaker2.html'
    form_class = CryptoPaymentForm

    def get_success_url(self):
        success_url = self.request.path_info

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CryptoPaymmentSimple, self).dispatch(request, *args, **kwargs)
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        mydate = timezone.now()
        context = super(CryptoPaymmentSimple, self).get_context_data()
        
        #unique_id is now deprecated
        context['unique_id'] = get_random_string(
            length=32) + str(int(time.mktime(mydate.timetuple())*1000))

        context['merchant_id'] = self.request.POST['merchant_id']
        context['item_name'] = self.request.POST['item_name']
        context['item_amount'] = self.request.POST['item_amount']
        context['item_number'] = self.request.POST['item_number']
        context['item_unique_id'] = self.request.POST['item_unique_id']
        context['item_qty'] = self.request.POST['item_qty']
        context['buyer_qty_edit'] = str(
            self.request.POST['buyer_qty_edit']).lower()
        context['invoice_number'] = self.request.POST['invoice_number']
        context['allow_shipping_cost'] = str(
            self.request.POST['allow_shipping_cost']).lower()
        context['success_url_link'] = self.request.POST['success_url_link']
        context['cancel_url_link'] = self.request.POST['cancel_url_link']
        context['ipn_url_link'] = self.request.POST['ipn_url_link']
        context['btn_image'] = self.request.POST['btn_image']
        context['allow_buyer_note'] = self.request.POST['allow_buyer_note']
        item_code = self.request.POST['item_unique_id']
        temp_id = context['merchant_id']
        # 
        item_obj = SimpleButtonItem.objects.get(item_unique_id = item_code)
        item_amount =  float(item_obj.item_amount)

        request.session['item_amount'] = item_amount
        # shipping_cost_add = item_obj.shipping_cost_add
        shipping_cost = item_obj.shipping_cost
        item_amount =  float(item_obj.item_amount)
        tax_amount = float(item_obj.item_tax) * float(self.request.POST['item_qty'])
        context['tax_amount'] = tax_amount
        item_qty = self.request.POST['item_qty']
        if (float(item_qty)>1):
            total_shipping = float(shipping_cost) * (float(item_qty)-1)
        else:
            total_shipping = float(shipping_cost)

        context['shipping_cost'] = total_shipping
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        return render(request, 'merchant_tools/payincryptobtnmaker2.html', context)

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
            if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
                total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
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
            item_uid=self.request.POST.get('item_unique_id',0)
            btn_item_obj = ButtonItem.objects.get(item_unique_id = item_uid)
            item_amount = btn_item_obj.item_amount

            item_qty = self.request.POST.get('item_quantity','')
            shipping_cost_add = btn_item_obj.shipping_cost_add
            shipping_cost = btn_item_obj.shipping_cost
            tax_amount = float(btn_item_obj.item_tax)* float(item_qty)
            print(btn_item_obj.item_tax)
            if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
                total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
            else:
                total_shipping = float(shipping_cost)
            
            context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
            context['item_total'] = round((float(item_qty) * float(item_amount)),2)


            try:
                temp_obj, created = ButtonInvoice.objects.get_or_create(
                    merchant_id = self.request.POST['merchant_id'],
                    unique_id = self.request.POST['unique_id'],
                    invoice_number = self.request.POST['invoice_number'],
                    item_name=btn_item_obj.item_name,
                    item_amount=context['payable'],
                    item_number=self.request.POST['item_number'],
                    item_qty=self.request.POST['item_qty'],
                    tax_amount=tax_amount,
                    shipping_cost=total_shipping,
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
        temp_id = temp_obj.merchant_id
        unique_id = temp_obj.unique_id
        if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
        else:
            total_shipping = float(shipping_cost)
        
        print ("1 total shipiing" + str(total_shipping))
        print("tax amount" + str(tax_amount))
        context['unique_id'] = unique_id
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

class DonationButtonMakerInvoice(TemplateView):
    template_name = 'merchant_tools/btncoinselect.html'


    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            self.invoice_url = self.kwargs['token']
        except:
            self.invoice_url = False
        return super(DonationButtonMakerInvoice, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        domain = self.request.get_host()
        context = super().get_context_data()
        if self.invoice_url:
            temp_obj = DonationButtonInvoice.objects.get(URL_link__icontains = self.invoice_url)
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
            if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
                total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
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
            reverse('mtools:donorbtnpay2', kwargs={'token': token})
        
        if not self.invoice_url:
            try:
                temp_obj, created = DonationButtonInvoice.objects.get_or_create(
                    merchant_id = self.request.POST['merchant_id'],
                    unique_id = self.request.POST['unique_id'],
                    invoice_number = self.request.POST['invoice_number'],
                    item_name=self.request.POST['item_name'],
                    item_amount=self.request.POST.get('item_amount', ''),
                    item_number=self.request.POST['item_number'],
                    item_qty=self.request.POST['item_qty'],
                    tax_amount=self.request.POST['tax_amount'],
                    shipping_cost=self.request.POST['shipping_cost'],
                    first_name=self.request.POST.get('first_name', ''),
                    last_name=self.request.POST.get('last_name', ''),
                    email_addr=self.request.POST.get('email_addr', ''),
                    addr_l1=self.request.POST.get('addr_l1', ''),
                    addr_l2=self.request.POST.get('addr_l2', ''),
                    country=self.request.POST.get('country', ''),
                    city=self.request.POST.get('city', ''),
                    zipcode=self.request.POST.get('zipcode', ''),
                    phone=self.request.POST.get('phone', ''),
                    buyer_note=self.request.POST.get('buyer_note', ''),
                    URL_link = html_url
                )
                if created:
                    temp_obj.save()  
            except:
                temp_obj = DonationButtonInvoice.objects.get(unique_id = self.request.POST['unique_id'])  
        else:
            try:
                self.invoice_url = domain + reverse('mtools:btnpay2', kwargs={'token': self.invoice_url})
                temp_obj = DonationButtonInvoice.objects.get(URL_link = self.invoice_url)
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
        if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
            total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
        else:
            total_shipping = float(shipping_cost)
        
        context['item_amount'] = item_amount
        context['unique_id'] = unique_id
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        # temp_obj.item_amount = context['payable']
        # temp_obj.save()
        #attempt payment
        check_prepaid = MultiPayment.objects.filter(paid_unique_id=unique_id)
        total_paid = 0
        if check_prepaid:
            total_paid = 0
            for prepaid in check_prepaid:
                total_paid = float(prepaid.recieved_usd)
        try:
            context['amt_remaining'] = context['payable'] - float(total_paid)                                     
        except:
            context['amt_remaining'] = context['payable']
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

class SimpleButtonMakerInvoice(TemplateView):
    template_name = 'merchant_tools/btncoinselect.html'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        try:
            self.invoice_url = self.kwargs['token']
        except:
            self.invoice_url = False
        context = super().get_context_data()
        return super(SimpleButtonMakerInvoice, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        domain = self.request.get_host()
        context = super().get_context_data(*args, **kwargs)
        try:
            rates = cache.get('rates')
            rates = ast.literal_eval(rates)
        except:
            data = json.loads(requests.get("http://coincap.io/front").text)
            rates = {rate['short']:rate['price'] for rate in data}
        print(rates)
        context['rates'] = json.dumps(rates)
        if self.invoice_url:
            temp_obj = SimpleButtonInvoice.objects.get(URL_link__icontains = self.invoice_url)
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
            if ((float(shipping_cost_add)) > 0 and float(item_qty)>1) :
                total_shipping = float(shipping_cost) + (float(shipping_cost_add) * (float(item_qty)-1))
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
            reverse('mtools:simplebtnpay2', kwargs={'token': token})
        
        if not self.invoice_url:
            try:
                temp_obj, created = SimpleButtonInvoice.objects.get_or_create(
                    merchant_id = self.request.POST['merchant_id'],
                    unique_id = self.request.POST['unique_id'],
                    invoice_number = self.request.POST['invoice_number'],
                    item_name=self.request.POST['item_name'],
                    item_amount=self.request.POST.get('item_amount', ''),
                    item_number=self.request.POST['item_number'],
                    item_qty=self.request.POST['item_qty'],
                    tax_amount=self.request.POST['tax_amount'],
                    shipping_cost=self.request.POST['shipping_cost'],
                    first_name=self.request.POST.get('first_name', ''),
                    last_name=self.request.POST.get('last_name', ''),
                    email_addr=self.request.POST.get('email_addr', ''),
                    addr_l1=self.request.POST.get('addr_l1', ''),
                    addr_l2=self.request.POST.get('addr_l2', ''),
                    country=self.request.POST.get('country', ''),
                    city=self.request.POST.get('city', ''),
                    zipcode=self.request.POST.get('zipcode', ''),
                    phone=self.request.POST.get('phone', ''),
                    buyer_note=self.request.POST.get('buyer_note', ''),
                    URL_link = html_url
                )
                if created:
                    temp_obj.save()  
            except:
                temp_obj = SimpleButtonInvoice.objects.get(unique_id = self.request.POST['unique_id'])  
        else:
            try:
                self.invoice_url = domain + reverse('mtools:btnpay2', kwargs={'token': self.invoice_url})
                temp_obj = SimpleButtonMakerInvoice.objects.get(URL_link = self.invoice_url)
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
        if (float(item_qty)>1):
            total_shipping = float(shipping_cost) * (float(item_qty)-1)
        else:
            total_shipping = float(shipping_cost)
        
        context['item_amount'] = item_amount
        context['unique_id'] = unique_id
        context['payable'] = (float(item_qty) * float(item_amount))+ total_shipping + float(tax_amount)
        context['item_total'] = round((float(item_qty) * float(item_amount)),2)
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        context['available_coins'] = coinlist.payment_gateway_coins()
        # temp_obj.item_amount = context['payable']
        # temp_obj.save()
        #attempt payment
        check_prepaid = MultiPayment.objects.filter(paid_unique_id=unique_id)
        total_paid = 0;
        if check_prepaid:
            total_paid = 0;
            for prepaid in check_prepaid:
                total_paid = float(prepaid.recieved_usd)
        try:
            context['amt_remaining'] = context['payable'] - float(total_paid)                                     
        except:
            context['amt_remaining'] = context['payable']
        attempted = 0
        try:
            for prepaid in check_prepaid:
                attempted = attempted + float(prepaid.attempted_usd) 
                
        except:
            pass
        context['attempted'] = attempted
        #attempt payment
        try:
            rates = redis_object.hgetall('rates')
            rates = ast.literal_eval(rates)
        except:
            data = json.loads(requests.get("http://coincap.io/front").text)
            rates = {rate['short']:rate['price'] for rate in data}
        context['rates'] = json.dumps(rates)

        context['url'] = temp_obj.URL_link
        context['available_coins'] = coinlist.payment_gateway_coins()
        return self.render_to_response(context)

class ButtonMakerPayView(TemplateView):
    template_name = 'merchant_tools/btnqrgenerator.html'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data()
        superuser = User.objects.filter(is_superuser=True).first()
        unique_id = request.POST.get('unique_id')
        selected_coin = request.POST.get('selected_coin')
        payable_amt = request.POST.get('coin_amt')
        payable_amt_usd = request.POST.get('payable_amt')
        try:
            merchant_id =  (SimpleButtonInvoice.objects.filter(unique_id = unique_id))[0].merchant_id
        except:
            try:
                merchant_id =  (ButtonInvoice.objects.filter(unique_id = unique_id))[0].merchant_id
            except:
                try:
                    merchant_id =  (DonationButtonInvoice.objects.filter(unique_id = unique_id))[0].merchant_id
                except Exception as e:
                    raise e

        # print( unique_id + ','+ selected_coin + ','+payable_amt + ','+payable_amt_usd)
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
            
                addr = create_wallet(Profile.objects.get(merchant_id=merchant_id).user, selected_coin, unique_id, True)
            

        request.session['crypto_address'] = addr
        try:
            obj, created = MultiPayment.objects.get_or_create(
                merchant_id = merchant_id,
                paid_amount=payable_amt,
                paid_in=Coin.objects.get(code=selected_coin),
                eq_usd=payable_amt_usd,
                paid_unique_id=unique_id,
                attempted_usd = payable_amt_usd,
                transaction_id=account_activation_token.make_token(
                    user=self.request.user),
                # paid_time=datetime.datetime.now(),
                payment_address=addr
            )
        except:
            obj, created = MultiPayment.objects.get_or_create(
                merchant_id = merchant_id,
                paid_amount=payable_amt,
                paid_in_erc=EthereumToken.objects.get(contract_symbol=selected_coin),
                eq_usd=payable_amt,
                paid_unique_id=unique_id,
                # paid_time=datetime.datetime.now(),
                attempted_usd = payable_amt,
                transaction_id=account_activation_token.make_token(
                    user=self.request.user),
                payment_address=addr
            )
            
        time_expiry = MultiPayment.objects.filter(paid_unique_id=unique_id)[0].paid_date + timedelta(hours=8)
        for_js = int(time.mktime(time_expiry.timetuple())) * 1000
        context['time_expiry'] = for_js
        context['unique_id'] = unique_id
        context['payable_amt'] = payable_amt
        context['payable_amt_usd'] = payable_amt_usd
        context['selected_coin'] = selected_coin
        context['crypto_address'] = addr
        return render(request, 'merchant_tools/btnqrgenerator.html', context)


class MTest(TemplateView):
    template_name='common/gcps_base.html'

    def get_context_data(self):
        context = super().get_context_data()
        input_cur = "BTC"
        amount = 0.05
        rates = cache.get('rates')
        rates['EXMR'] = 0.017
        cur_rate = rates[input_cur]
        cur_cost = amount * cur_rate
        print("current_cost %s",cur_cost)
        try:
            input_coin = Coin.objects.get(code = input_cur)
        except:
            input_coin = EthereumToken.objects.get(contract_symbol = input_cur)
        tradecommission_obj =  TradeCommision.objects.all().first()
        trans_charge_type = tradecommission_obj.transaction_commission_type
        exmr_rate = rates['EXMR']
        if trans_charge_type == "FLAT":
            print("use flat slab logic")
            exmr_amount = float(tradecommission_obj.commission_flat_rate)
        else:
            print("use percentage logic")
            transaction_charge_usd = float(tradecommission_obj.commission_percentage) * cur_cost
            exmr_amount = transaction_charge_usd/exmr_rate
        
        print(exmr_amount)
        return context


        # wallet_list = Wallet.objects.all()
        # for wallet in wallet_list:
        #     import pdb; pdb.set_trace()
        #     for addr in wallet.addresses.all():
        #         temp_bal = get_balance(wallet.user, wallet.name, addr.address)
        #         cache.set(addr.address,temp_bal)
        #         temp_obj = WalletAddress.objects.get(address=addr.address)
        #         temp_obj.last_check = datetime.datetime.now()
        #         temp_obj.current_balance = temp_bal
        #         temp_obj.save()
        # context = super(MTest, self).get_context_data()
        # print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        # print(cache.get(0x810561bdd3876b7a005e64f9ca759a0febdda5e9))
        # print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        # context['eth_bal'] = cache.get("0x810561bdd3876b7a005e64f9ca759a0febdda5e9")