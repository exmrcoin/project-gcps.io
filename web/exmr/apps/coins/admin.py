from django.contrib import admin

from apps.coins.models import Coin, CoinSetting, CoinVote

admin.site.register(Coin)
admin.site.register(CoinVote)
admin.site.register(CoinSetting)
