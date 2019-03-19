from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from apps.store.models import StoreCategory, Store, Rating


class StoreCategoryResource(resources.ModelResource):

    class Meta:
        model = StoreCategory
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'name', 'image')


class StoreCategoryAdmin(ImportExportModelAdmin):
    """
        Custom admin for model store category
    """

    resource_class = StoreCategoryResource
    list_display = ['name', 'publish']
    list_editable = ['publish']
    list_filter = ['publish']
    prepopulated_fields = {"slug": ("name",)}


class StoreAdmin(admin.ModelAdmin):
    """
    Custom admin for model store
    """
    list_display = ['store_name', 'category', 'is_approved']
    list_editable = ['is_approved']
    list_filter = ['is_approved']


admin.site.register(StoreCategory, StoreCategoryAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Rating)

