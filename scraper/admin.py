from django.contrib import admin

from scraper.models import TikTokVideo, TikTokUser, Hashtag


@admin.register(TikTokVideo)
class TikTokVideoAdmin(admin.ModelAdmin):
    pass

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass

@admin.register(TikTokUser)
class TikTokUserAdmin(admin.ModelAdmin):
    pass
