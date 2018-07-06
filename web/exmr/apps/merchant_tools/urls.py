from django.urls import path
from django.views.generic import TemplateView

from apps.merchant_tools.views import ButtonMakerView,CryptoPaymment,PaymentFormSubmitView

app_name = 'mtools'

urlpatterns = [
    path('buttonmaker/', ButtonMakerView.as_view(),  name='buttonmaker'),
    path('make-payment/', CryptoPaymment.as_view(),  name='cryptopay'),
    path('payment-process-1/', PaymentFormSubmitView.as_view(),  name='payprocess')

]