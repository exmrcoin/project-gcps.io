from django.urls import path
from django.views.generic import TemplateView

from apps.merchant_tools.views import (ButtonMakerView, CryptoPaymment, PaymentFormSubmitView, MercDocs,
                                       URLMakerView, URLMakerInvoiceView, POSQRMakerView, POSQRPayView, POSQRCompletePaymentView)

app_name = 'mtools'

urlpatterns = [
    path('buttonmaker/', ButtonMakerView.as_view(),  name='buttonmaker'),
    path('urlmaker/', URLMakerView.as_view(),  name='urlmaker'),
    path('invoice/<token>/', URLMakerInvoiceView.as_view(),  name='urlmakerinvoice'),
    path('make-payment/', CryptoPaymment.as_view(),  name='cryptopay'),
    path('payment-process-1/', PaymentFormSubmitView.as_view(),  name='payprocess'),
    path('merchant-tools-docs/', MercDocs.as_view(),  name='mercdocs'),
    path('pos-qr/', POSQRMakerView.as_view(),  name='posqrmaker'),
    path('pos-qr/<token>/', POSQRPayView.as_view(),  name='pospay'),
    path('POSQRCompletePayment/', POSQRCompletePaymentView.as_view(),  name='posqrpay')
]
