from django.contrib import admin
from sorl.thumbnail import get_thumbnail
from django.template.loader import render_to_string
# Register your models here.
from apps.merchant_tools.models import ButtonImage, ButtonMaker


class ButtonImageAdmin(admin.ModelAdmin):
    list_display = ('label','thumb')

    def thumb(self, obj):
        return  render_to_string('thumb.html',{
                    'image': obj.btn_img
                })

    thumb.allow_tags = True


admin.site.register(ButtonMaker)
admin.site.register(ButtonImage, ButtonImageAdmin)
