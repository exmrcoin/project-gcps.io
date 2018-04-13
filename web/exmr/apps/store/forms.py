from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

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



    def clean(self):
        if not self.cleaned_data.get('username_or_merch_id'):
            raise forms.ValidationError(_('Either username or email needs to be provided'))
        else:
            username_or_merch_id = self.cleaned_data.get('username_or_merch_id')
            user = User.objects.filter(username=username_or_merch_id)
        if not user:
            profile = Profile.objects.filter(merchant_id=username_or_merch_id)
        if not profile:
            raise forms.ValidationError(_('User not found'))
