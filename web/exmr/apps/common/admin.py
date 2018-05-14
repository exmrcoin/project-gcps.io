from django.contrib import admin

from apps.common.models import Currency, SocialLink, HelpSidebar, FAQ, LegalSidebar

admin.site.register(Currency)
admin.site.register(SocialLink)
admin.site.register(HelpSidebar)
admin.site.register(FAQ)
admin.site.register(LegalSidebar)
