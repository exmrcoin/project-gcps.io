from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from apps.coins.models import Coin, CoinSetting, CoinVote, CoinConvertRequest, Wallet


class CoinResource(resources.ModelResource):

    class Meta:
        model = Coin
        import_id_field = 'code'
        export_id_field = 'code'
        skip_unchanged = True
        report_skipped = True
        fields = ('id', 'coin_name', 'code', 'confirms', 'to_btc', 'fee_percentage')


class CoinModelAdmin(ImportExportModelAdmin):

    resource_class = CoinResource
    search_fields = ('code', 'coin_name', )
    list_display = ('coin_name', 'code', 'confirms', 'active')
    list_editable = ('active', )

    class Meta:
        model = Coin


admin.site.register(Coin, CoinModelAdmin)
admin.site.register(CoinVote)
admin.site.register(CoinSetting)
admin.site.register(CoinConvertRequest)
admin.site.register(Wallet)
