from django.urls import path
from django.views.generic import TemplateView

from apps.common.views import CoinRequestView, HelpTemplateView, HelpView, Update,\
                              PluginDownloadView, StaticPageView

app_name = 'common'

urlpatterns = [
    path('coin-hosting/', CoinRequestView.as_view(),  name='coinhosting'),
    path('help/', HelpView.as_view(), name='help'),
    path('help/<slug:slug>/', HelpTemplateView.as_view(), name='helptopic'),
    path('plugin-download/', PluginDownloadView.as_view(), name='plugin-download'),
    path('update/', Update.as_view(), name='update'),
    path('docs/<slug>/', StaticPageView.as_view(), name='staticpage')
]
