from django import forms

from apps.merchant_tools.models import ButtonMaker, CryptoPaymentRec, URLMaker


class ButtonMakerForm(forms.ModelForm):
    class Meta:
        model = ButtonMaker
        exclude = ['']

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

    def __init__(self, *args, **kwargs):
        super(URLMakerForm, self).__init__(*args, **kwargs)
        self.fields['merchant_id'].disabled = True