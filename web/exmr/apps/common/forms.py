from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import CoinRequest, ContactUs

class CoinRequestForm(ModelForm):
    
    """
    Form for updating Mobile Number.

    """
    class Meta:
        model = CoinRequest
        fields = '__all__'

class ContactForm(ModelForm):
	"""
	Form for contact us
	"""

	class Meta:
		model = ContactUs
		fields = '__all__'