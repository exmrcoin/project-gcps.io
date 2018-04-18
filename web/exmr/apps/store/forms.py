from django import forms
from django.contrib.auth.models import User
from apps.accounts.models import Profile
from apps.store.models import Store, StoreCategory
from django.utils.translation import ugettext_lazy as _


class AddStoreForm(forms.ModelForm):

    username_or_merch_id = forms.CharField()
    category = forms.ModelChoiceField(queryset=StoreCategory.objects.filter(publish=True), initial='Please Select')

    class Meta:
        model = Store
        fields = ['store_name','store_url','category','crypto_processor','store_email',
                  'keywords', 'banner_image_url']

    def clean_username_or_merch_id(self):
        username_or_merch_id = self.cleaned_data.get('username_or_merch_id')
        if not username_or_merch_id:
            raise forms.ValidationError(_('Either username or email needs to be provided'))
        if Profile.objects.filter(merchant_id=username_or_merch_id).exists():
            return username_or_merch_id
        elif Profile.objects.filter(user__username=username_or_merch_id).exists():
            return username_or_merch_id
        raise forms.ValidationError(_('User not found'))

