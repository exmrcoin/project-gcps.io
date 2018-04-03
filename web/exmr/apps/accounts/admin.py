from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Profile, Address, Feedback, ProfileActivation, NewsLetter
from exmr import settings


class ProfileAdmin(admin.ModelAdmin):
    """
    Admin customization settings for profile model
    """
    list_display = ['user', 'timezone', 'get_two_factor_auth_display', 'merchant_id']

    fieldsets = (
        (_('Basic Details'), {
            'fields': ('user', 'gender', 'timezone', 'date_format','time_format','is_subscribed')
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


def send_newsletter(self, request, queryset):
    profiles = Profile.objects.filter(is_subscribed=True)
    for q in queryset:
        subject = q.subject
        content = q.content
        from_email = settings.EMAIL_HOST_USER
    if profiles:
        for profile in profiles:
            email = profile.user.email
            msg = EmailMultiAlternatives(subject, '', from_email, [email])
            msg.attach_alternative(content, "text/html")
            msg.send()

send_newsletter.short_description = 'Send newsletters'

class NewsletterAdmin(admin.ModelAdmin):
    actions = [send_newsletter, ]

admin.site.register(NewsLetter, NewsletterAdmin)


