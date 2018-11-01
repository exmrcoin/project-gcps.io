from django import forms
from apps.coins.models import Coin
from apps.merchant_tools.models import ButtonMaker, CryptoPaymentRec, URLMaker, POSQRMaker, DonationButtonMaker, ButtonImage, SimpleButtonMaker
from django.utils.safestring import mark_safe
from django.core.validators import DecimalValidator, URLValidator, ValidationError
from django_select2.forms import Select2MultipleWidget
from django.forms import Select

class CustomChoiceField(forms.ModelChoiceField):
    
    def label_from_instance(self, obj):
        return mark_safe("<span> &emsp;&emsp;   %s</span><img class='img-responsive w100px floatr ' style='margin-left: 30px;' src='%s'/> <br>"% (str(obj.label), obj.btn_img.url))


class ButtonMakerForm(forms.ModelForm):
    btn_image = CustomChoiceField(widget=forms.RadioSelect, queryset=ButtonImage.objects.all(), empty_label=None)

    class Meta:
        model = ButtonMaker
        exclude = ['']
        labels = {
        "item_amount":"Price in USD $"
        }

    def __init__(self, *args, **kwargs):
        super(ButtonMakerForm, self).__init__(*args, **kwargs)
        if self.fields['merchant_id']:
            self.fields['merchant_id'].disabled = True
        # self.fields['btn_image']=forms.ModelChoiceField(queryset=ButtonImage.objects.all())

class SimpleButtonMakerForm(forms.ModelForm):
    btn_image = CustomChoiceField(widget=forms.RadioSelect, queryset=ButtonImage.objects.all(), empty_label=None)

    class Meta:
        model = SimpleButtonMaker
        exclude = ['']
        labels = {
        "item_amount":"Price in USD $"
        }

    def __init__(self, *args, **kwargs):
        super(SimpleButtonMakerForm, self).__init__(*args, **kwargs)
        if self.fields['merchant_id']:
            self.fields['merchant_id'].disabled = True
        # self.fields['btn_image']=forms.ModelChoiceField(queryset=ButtonImage.objects.all())        

class DonationButtonMakerForm(forms.ModelForm):
    btn_image = CustomChoiceField(widget=forms.RadioSelect, queryset=ButtonImage.objects.all(), empty_label=None)
    
    class Meta:
        model = DonationButtonMaker
        exclude = []
        labels = {
        "item_amount":"Price in USD $"
        }

    def __init__(self, *args, **kwargs):
        super(DonationButtonMakerForm, self).__init__(*args, **kwargs)
        if self.fields['merchant_id']:
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
