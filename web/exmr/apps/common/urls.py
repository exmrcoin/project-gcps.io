from django.urls import path
from django.views.generic import TemplateView

from apps.common.views import CoinRequestView, HelpTemplateView, HelpView

app_name = 'common'

urlpatterns = [
    path('coin-hosting/', CoinRequestView.as_view(),  name='coinhosting'),
    path('help/', HelpView.as_view(), name='help'),
    path('help/<slug:slug>/', HelpTemplateView.as_view(), name='helptopic'),
]
