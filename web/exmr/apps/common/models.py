from ckeditor.fields import RichTextField, RichTextFormField
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

AUTH_TYPE = (
    ('HTTP Auth', _('HTTP Auth')),
    ('HMAC', _('HMAC')),
    ('N/A', _('N/A')),
)


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


class CoinRequest(models.Model):
    """
    Model to save incoming request for coins
    """
    requester_name = models.CharField(max_length=64)
    requester_email = models.EmailField()
    coin_symbol = models.CharField(max_length=10)
    coin_name = models.CharField(max_length=64)
    coin_url = models.CharField(max_length=128)
    coin_algorithm = models.CharField(max_length=255)
    coin_source_url = models.CharField(max_length=128)
    
    def __str__(self):
        return self.coin_name

class FAQ(models.Model):
    """
    Model to save frequently asked questions
    """
    faq_question = models.CharField(max_length=512)
    faq_answer = models.TextField()

    def __str__(self):
        return self.faq_question


class HelpSidebar(models.Model):
    """
    Model to save help sidebar topics and their answers
    """
    help_topic = models.CharField(max_length=64)
    help_answer = RichTextUploadingField()
    order_index = models.IntegerField()
    slug = models.SlugField(default=slugify(help_topic))

    def __str__(self):
        return self.help_topic

    def save(self, *args, **kwargs):
        self.slug = slugify(self.help_topic)
        super(HelpSidebar, self).save(*args, **kwargs)


class LegalSidebar(models.Model):
    """
    Model to save help sidebar topics and their answers
    """
    help_topic = models.CharField(max_length=64)
    help_answer = RichTextUploadingField()
    order_index = models.IntegerField()
    slug = models.SlugField(default=slugify(help_topic))

    def __str__(self):
        return self.help_topic

    def save(self, *args, **kwargs):
        self.slug = slugify(self.help_topic)
        super(LegalSidebar, self).save(*args, **kwargs)


class PluginDownload(models.Model):
    """
    Model to Save details in merchant tools plugins option
    """
    shopping_cart_logo = models.ImageField(_('image'))
    last_update = models.DateField(auto_now_add=True)
    download_url = models.URLField(_('link'))
    auth_type = models.CharField(max_length=10)
    zero_confirm = models.BooleanField(blank=True)
    video_url = models.URLField(_('Video URL'))


class StaticPage(models.Model):
    page_name = models.CharField(max_length=128, unique=True)
    topic = models.CharField(max_length=128)
    content = RichTextUploadingField()
    slug = models.SlugField(default=slugify(page_name))

    def __str__(self):
        return self.page_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.page_name)
        super(StaticPage, self).save(*args, **kwargs)

class ContactUs(models.Model):
    name = models.CharField(null=False, max_length=100)
    email = models.EmailField(null=False)
    category = models.CharField(max_length=30, null=True)
    message = models.TextField()
    
    def __str__(self):
        return self.name