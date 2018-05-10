from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import CoinRequest

class CoinRequestForm(ModelForm):
    
    """
    Form for updating Mobile Number.

    """
    class Meta:
        model = CoinRequest
        fields = '__all__'