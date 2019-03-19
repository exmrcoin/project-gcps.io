from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Profile, Address, Feedback, ProfileActivation, NewsLetter, KYC,\
                                 TwoFactorAccount, KYCTerms
from apps.accounts.tasks import send_newsletter
from exmr import settings


class ProfileAdmin(admin.ModelAdmin):
    """
    Admin customization settings for profile model
    """
    list_display = ['user', 'timezone', 'get_two_factor_auth_display', 'merchant_id']

    fieldsets = (
        (_('Basic Details'), {
            'fields': ('user', 'gender', 'timezone', 'date_format','time_format','is_subscribed','refered_by')
        }),
        (_('Public Info'), {
            'fields': ('public_name', 'public_email', 'public_url', 'use_gravatar'),
        }),
        (_('Login Security'), {
            'fields': ('pgp_gpg_public_key', 'two_factor_auth', 'email_confirmation_transaction'),
        }),

    )


admin.site.register(Profile, ProfileAdmin)


class AddressAdmin(admin.ModelAdmin):
    """
    Custom admin for model address
    """
    list_display = ['address_name', 'is_default']


admin.site.register(Address, AddressAdmin)


class FeedbackAdmin(admin.ModelAdmin):
    """
    Custom admin for model feedback
    """
    list_display = ['user', 'rating', 'left_by', 'blocked']
    list_editable = ['blocked']
    list_filter = ['blocked']


admin.site.register(Feedback, FeedbackAdmin)

admin.site.register(ProfileActivation)



send_newsletter.short_description = 'Send newsletters'

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['subject', 'content']
    actions = [send_newsletter]

admin.site.register(TwoFactorAccount)
admin.site.register(NewsLetter, NewsletterAdmin)
admin.site.register(KYC)
admin.site.register(KYCTerms)



