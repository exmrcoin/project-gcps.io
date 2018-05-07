from django.urls import path
from django.views.generic import TemplateView

from apps.coins import views as coin_views
from apps.accounts.forms import CustomPasswordResetForm

app_name = 'coins'

urlpatterns = [
    path('supported/', coin_views.SupportedCoinView.as_view(), name='supported_coins'),
    path('newaddr/', coin_views.NewCoinAddr.as_view(), name='newaddr'),
    path('coin-conversion/<str:from>/<str:to>/', coin_views.ConvertCoinsView.as_view(), name='coin_conversion'),
    path('coin-conversion-confirm/', coin_views.CoinConversionFinalView.as_view(), name='conversion_final'),
    path('checkout/', TemplateView.as_view(template_name='coins/coin-checkout.html')),
    path('add-coin/', coin_views.AddNewCoin.as_view(), name = 'add-coin'),
]
