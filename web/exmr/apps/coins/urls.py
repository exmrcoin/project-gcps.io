from django.urls import path
from django.views.generic import TemplateView

from apps.coins import views as coin_views
from apps.accounts.forms import CustomPasswordResetForm

app_name = 'coins'

urlpatterns = [
    path('wallets/', coin_views.WalletsView.as_view(), name='wallets'),
    path('supported/<str:type>/', coin_views.SupportedCoinView.as_view(),
         name='supported_coins'),
    path('newaddr/<str:currency>/', coin_views.NewCoinAddr.as_view(), name='newaddr'),
    path('coin-conversion/<str:from>/<str:to>/',
         coin_views.ConvertCoinsView.as_view(), name='coin_conversion'),
    path('coin-conversion-confirm/',
         coin_views.CoinConversionFinalView.as_view(), name='conversion_final'),
    path('checkout/', TemplateView.as_view(template_name='coins/coin-checkout.html')),
    path('add-coin/', coin_views.AddNewCoin.as_view(), name='add-coin'),
    path('coin-settings/',coin_views.CoinSettings.as_view(),name='coin-settings'),
    path('coin-withdrawal/<str:code>/', coin_views.CoinWithdrawal.as_view(), name='coin-withdrawal'),
    path('send/<slug:slug>/', coin_views.SendView.as_view(), name='send'),
    path('send-success/', coin_views.SendSuccessView.as_view(), name='send-success'),
    path('sendconfirm/<slug:slug>/', coin_views.SendConfirmView.as_view(), name='sendconfirm'),
    path('vote-details/<str:currency>/', coin_views.VoteDetailsView.as_view(), name='vote-details'),
    path('refund-claim/<slug:slug>/', coin_views.RefundClaimView.as_view(), name='refund-claim'),
    path('add-public-coin/', coin_views.NewCoinAddView.as_view(), name='add-public-coin' ),
    path('paybyname/', coin_views.PayByNameView.as_view(), name='paybyname' ),
    path('paybyname-payment/', coin_views.PayByNamePayView.as_view(), name='paybyname-payment' ),
    path('copromotion-form/', coin_views.CopromotionView.as_view(), name="copromotion-form"),
    path('get_balance/', coin_views.BalanceView.as_view(), name="get_balance"),
    path('coin-vote-winners/', coin_views.VoteWinners.as_view(), name="winners"),
    path('coin-convert/<str:currency>', coin_views.CoinConvertView.as_view(), name="convert_select"),
    path('coin-convert-confirmation/', coin_views.CoinConvertView2.as_view(), name="convert_select_confirm"),
    path('coin-convert-complete/', coin_views.CoinConvertView3.as_view(), name="convert_select_finish"),
    path('currency-convert/', coin_views.ConversionView.as_view(), name="currency_convert"),
    path('insufficient/', TemplateView.as_view(template_name='coins/no-money.html'), name="low-balance"),
    path('paypal-checkout/', coin_views.PayPalCheckoutView.as_view(), name="paypal_checkout"),
    path('paypal-verify/', coin_views.PayPalVerifyView.as_view(), name="paypal_verify"),
    path('buy-coin/<str:currency>/',coin_views.BuyCryptoView.as_view(), name="buy_coin"),


]
