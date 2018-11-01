from django.urls import path
from django.views.generic import TemplateView

from apps.merchant_tools.views import (ButtonMakerView, CryptoPaymment, PaymentFormSubmitView, MercDocs,
                                       URLMakerView, URLMakerInvoiceView, POSQRMakerView, POSQRPayView, POSQRCompletePaymentView,ButtonMakerPayView,
                                       HelpTemplateView, DonationButtonMakerView, SimpleButtonMakerView, ButtonMakerContinuePayment, ButtonMakerInvoice, CryptoPaymmentV2, DonationButtonMakerInvoice, CryptoPaymmentSimple, SimpleButtonMakerInvoice)
app_name = 'mtools'

urlpatterns = [
    path('buttonmaker/', ButtonMakerView.as_view(),  name='buttonmaker'),
    path('donationbuttonmaker/', DonationButtonMakerView.as_view(),  name='donationbuttonmaker'),
    path('simplebuttonmaker/', SimpleButtonMakerView.as_view(),  name='simplebuttonmaker'),
    path('urlmaker/', URLMakerView.as_view(),  name='urlmaker'),
    path('invoice/<token>/', URLMakerInvoiceView.as_view(),  name='urlmakerinvoice'),
    path('make-payment/', CryptoPaymment.as_view(),  name='cryptopay'), 
    path('payment-process-1/', PaymentFormSubmitView.as_view(),  name='payprocess'),
    path('merchant-tools-docs/', MercDocs.as_view(),  name='mercdocs'),
    path('help/<slug:slug>/', HelpTemplateView.as_view(), name='helptopic'),
    path('pos-qr/', POSQRMakerView.as_view(),  name='posqrmaker'),
    path('pos-qr/<token>/', POSQRPayView.as_view(),  name='pospay'),
    path('POSQRCompletePayment/', POSQRCompletePaymentView.as_view(),  name='posqrpay'),
    path('update-btn-form/', ButtonMakerContinuePayment.as_view(),  name='updatebtnmaker'),
    path('button-payment/', CryptoPaymmentV2.as_view(),  name='cryptopayV2'),
    path('simple-button-payment/', CryptoPaymmentSimple.as_view(),  name='cryptopaysimple'),
    path('donation-button-invoice-generate/', DonationButtonMakerInvoice.as_view(),  name='donorbtnpay'),
    path('simple-button-invoice-generate/', SimpleButtonMakerInvoice.as_view(),  name='simplebtnpay'),
    path('button-invoice-generate/', ButtonMakerInvoice.as_view(),  name='btnpay'),
    path('button-invoice-generate/<token>/', ButtonMakerInvoice.as_view(),  name='btnpay2'),
    path('simple-invoice-generate/<token>/', SimpleButtonMakerInvoice.as_view(),  name='simplebtnpay2'),
    path('donation-button-invoice-generate/<token>/', DonationButtonMakerInvoice.as_view(),  name='donorbtnpay2'),
    path('button-invoice-payment/', ButtonMakerPayView.as_view(),  name='btnqrcode'),
]
