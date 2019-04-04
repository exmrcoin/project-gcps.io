from django.urls import path
from django.views.generic import TemplateView

from apps.common.views import CoinRequestView, HelpTemplateView, HelpView, Update,\
                              PluginDownloadView, StaticPageView, ApiView, ApiTemplateView, ModeChangeView

app_name = 'common'

urlpatterns = [
    path('coin-hosting/', CoinRequestView.as_view(),  name='coinhosting'),
    path('api/', ApiView.as_view(), name='api'),
    path('api/<slug:slug>/', ApiTemplateView.as_view(), name='apitopic'),
    path('help/', HelpView.as_view(), name='help'),
    path('help/<slug:slug>/', HelpTemplateView.as_view(), name='helptopic'),
    path('plugin-download/', PluginDownloadView.as_view(), name='plugin-download'),
    path('update/', Update.as_view(), name='update'),
    path('coming-soon/', TemplateView.as_view(template_name='common/beta.html'), name='beta'),
    path('docs/<slug>/', StaticPageView.as_view(), name='staticpage'),
    path('change_color/', ModeChangeView.as_view(), name='change_mode')
]
