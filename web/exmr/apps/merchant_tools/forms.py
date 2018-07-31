from django import forms

from apps.coins.models import Coin
from apps.merchant_tools.models import ButtonMaker, CryptoPaymentRec, URLMaker, POSQRMaker
from django.core.validators import DecimalValidator, URLValidator, ValidationError

class ButtonMakerForm(forms.ModelForm):
    class Meta:
        model = ButtonMaker
        exclude = ['']
        labels = {
        "item_amount":"Price in USD $"
        }

    def __init__(self, *args, **kwargs):
        super(ButtonMakerForm, self).__init__(*args, **kwargs)
        self.fields['merchant_id'].disabled = True


class CryptoPaymentForm(forms.Form):
    class Meta:
        model = CryptoPaymentRec
        exclude = ['']


class URLMakerForm(forms.ModelForm):
    class Meta:
        model = URLMaker
        exclude = ['unique_id', 'URL_link']
        labels = {
        "item_amount":"Price in USD $"
        }

    def __init__(self, *args, **kwargs):
        super(URLMakerForm, self).__init__(*args, **kwargs)
        self.fields['merchant_id'].disabled = True


class POSQRForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (POSQRForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['currency'].queryset = Coins.objects.all()
        
    class Meta:
        model = POSQRMaker
        exclude=['URL_link','time_limit']

    def __init__(self, *args, **kwargs):
        super(POSQRForm, self).__init__(*args, **kwargs)
        self.fields['merchant_id'].disabled=True
        self.fields['unique_id'].disabled=True
