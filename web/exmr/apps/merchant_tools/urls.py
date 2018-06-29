from django.urls import path
from django.views.generic import TemplateView

from apps.merchant_tools.views import ButtonMakerView

app_name = 'mtools'

urlpatterns = [
    path('buttonmaker/', ButtonMakerView.as_view(),  name='buttonmaker')

]