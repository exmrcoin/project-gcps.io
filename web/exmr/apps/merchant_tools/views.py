import time
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, CreateView, View
from django.contrib.sites.models import Site
from apps.accounts.models import Profile
from apps.coins.models import Coin, WalletAddress
from apps.coins.utils import *
from apps.merchant_tools.forms import ButtonMakerForm, CryptoPaymentForm
from apps.merchant_tools.models import ButtonImage, ButtonMaker, CryptoPaymentRec, MercSidebarTopic
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.utils import timezone
# Create your views here.


class ButtonMakerView(FormView):

    template_name = 'merchant_tools/buttonmaker.html'
    form_class = ButtonMakerForm

    def get_success_url(self):
        success_url = self.request.path_info

    def get_initial(self):
        initial = super(ButtonMakerView, self).get_initial()
        initial['merchant_id'] = Profile.objects.get(
            user=self.request.user).merchant_id
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
        temp_html = ['<form action="//'+domain+reverse('mtools:cryptopay') + '" method="POST" >',
                     '<input type="hidden" name="merchant_id" value="'+merchant_id +
                     '" maxlength="128" disabled id="id_merchant_id" required />',
                     '<input type="hidden" name="item_name" value="'+item_name +
                     '" maxlength="128" id="id_item_name" required />',
                     '<input type="hidden" name="item_amount" value="'+item_amount +
                     '" maxlength="128" id="id_item_amount" required />',
                     '<input type="hidden" name="item_number" value="'+item_number +
                     '" maxlength="128" id="id_item_number" required />',
                     '<input type="hidden" name="item_qty" value="'+item_qty +
                     '" maxlength="128" id="id_item_qty" required />',
                     '<input type="hidden" name="buyer_qty_edit" value="' +
                     buyer_qty_edit+'" id="id_buyer_qty_edit" />',
                     '<input type="hidden" name="invoice_number" value="'+invoice_number +
                     '" maxlength="128" id="id_invoice_number" required />',
                     '<input type="hidden" name="tax_amount" value="'+tax_amount +
                     '" maxlength="128" id="id_tax_amount" required />',
                     '<input type="hidden" name="allow_shipping_cost" value="' +
                     allow_shipping_cost+'"id="id_allow_shipping_cost" />',
                     '<input type="hidden" name="shipping_cost" value="'+shipping_cost +
                     '" maxlength="128" id="id_shipping_cost" required />',
                     '<input type="hidden" name="shipping_cost_add" value="'+shipping_cost_add +
                     '" maxlength="128" id="id_shipping_cost_add" required />',
                     '<input type="hidden" name="success_url_link" value="'+success_url_link +
                     '" maxlength="128" id="id_success_url_link" required />',
                     '<input type="hidden" name="cancel_url_link" value="'+cancel_url_link +
                     '" maxlength="128" id="id_cancel_url_link" required />',
                     '<input type="hidden" name="ipn_url_link" value="'+ipn_url_link +
                     '" maxlength="128" id="id_ipn_url_linl" required />',
                     '<input type="hidden" name="allow_buyer_note" value="' +
                     allow_buyer_note+'"id="id_allow_buyer_note" />',
                     '<input type="hidden" name="btn_image" value="1"id="id_btn_image" />',
                     ]

        img_temp = ButtonImage.objects.get(label=btn_image)
        img_src = str(domain+img_temp.btn_img.url)
        link_html = '<input type="image" src="'+img_src + \
            '" alt="Buy Now with CoinPayments.net"></form>'
        context['btn_code'] = temp_html
        context['submit_image'] = link_html
        return render(self.request, 'merchant_tools/buttonmaker.html', context)


class CryptoPaymment(FormView):
    template_name = 'merchant_tools/payincrypto.html'
    form_class = CryptoPaymentForm

    def get_success_url(self):
        success_url = self.request.path_info

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(CryptoPaymment, self).dispatch(request, *args, **kwargs)

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
        context['merchant_name'] = Profile.objects.get(merchant_id=temp_id)
        return render(request, 'merchant_tools/payincrypto.html', context)


class PaymentFormSubmitView(View):
    def post(self, request, *args, **kwargs):

        sel_coin = Coin.objects.get(code=self.request.POST['selected_coin'])
        superuser = User.objects.get(is_superuser=True)
        crypto_address = create_wallet(superuser, sel_coin.code)
        # crypto_address = '123'
        print(crypto_address)
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
        temp_obj.save()
        context = {}
        # import pdb ; pdb.set_trace()
        merchant_id = self.request.POST['merchant_id']
        context['merchant_name'] = Profile.objects.get(merchant_id=merchant_id)
        context['crypto_address'] = crypto_address
        context['unique_id']=self.request.POST['unique_id']
        return render(request, 'merchant_tools/postpayment.html', context)


class MercDocs(TemplateView):
    template_name = 'merchant_tools/merc-help.html'

    def get_context_data(self):
        context = super().get_context_data();
        context['merc_sidebar_topic'] = MercSidebarTopic.objects.all()
        return context
