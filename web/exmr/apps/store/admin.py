from django.contrib import admin

# Register your models here.
from apps.store.models import StoreCategory, Store


class StoreCategoryAdmin(admin.ModelAdmin):
    """
        Custom admin for model store category
    """
    list_display = ['name', 'publish']
    list_editable = ['publish']
    list_filter = ['publish']
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(StoreCategory, StoreCategoryAdmin)


class StoreAdmin(admin.ModelAdmin):
    """
    Custom admin for model store
    """
    list_display = ['store_name', 'category', 'is_approved']
    list_editable = ['is_approved']
    list_filter = ['is_approved']


admin.site.register(Store, StoreAdmin)
