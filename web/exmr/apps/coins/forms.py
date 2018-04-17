from django import forms

from apps.coins.models import CoinConvertRequest


class ConvertRequestForm(forms.ModelForm):
    """
    Form used to save the coin requests
    """

    class Meta:
        model = CoinConvertRequest
        exclude = ('wallet_from', 'wallet_to')
