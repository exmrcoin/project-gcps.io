from django.urls import path

from apps.coins import views as coin_views
from apps.accounts.forms import CustomPasswordResetForm

app_name = 'coins'

urlpatterns = [
    path('supported/', coin_views.SupportedCoinView.as_view(), name='supported_coins'),
    path('coin-conversion/<slug:from>/<slug:to>', coin_views.SupportedCoinView.as_view(), name='coin_conversion'),
    path('coin-conversion-confirm/', coin_views.CoinConversionFinalView.as_view(), name='conversion_final'),

]
