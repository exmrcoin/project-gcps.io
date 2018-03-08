from django.db import models
from django.utils.translation import ugettext_lazy as _


class Currency(models.Model):
    """
    Model to save different currencies
    """
    name = models.CharField(_('name'), max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')


class SocialLink(models.Model):
    """
    Model to save different social media link
    """
    provider = models.CharField(_('provider'), max_length=255)
    link = models.URLField(_('link'))
    publish = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')

    def __str__(self):
        return self.provider
