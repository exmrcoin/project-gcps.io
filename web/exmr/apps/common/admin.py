from django.contrib import admin

from apps.common.models import Currency, SocialLink, HelpSidebar, FAQ, LegalSidebar,\
                               PluginDownload, StaticPage, ContactUs, CoinRequest, API, InformationalSidebar, ReceivingSidebar, AnnouncementHome

admin.site.register(Currency)
admin.site.register(SocialLink)
admin.site.register(HelpSidebar)
admin.site.register(FAQ)
admin.site.register(LegalSidebar)
admin.site.register(PluginDownload)
admin.site.register(StaticPage)
admin.site.register(ContactUs)
admin.site.register(CoinRequest)
admin.site.register(API)
admin.site.register(InformationalSidebar)
admin.site.register(ReceivingSidebar)
admin.site.register(AnnouncementHome)
