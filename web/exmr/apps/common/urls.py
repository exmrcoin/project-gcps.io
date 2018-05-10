from django.urls import path
from django.views.generic import TemplateView

from apps.common.views import CoinRequestView

app_name = 'common'

urlpatterns = [
    path('coin-hosting/', CoinRequestView.as_view(),  name='coinhosting'),
]
