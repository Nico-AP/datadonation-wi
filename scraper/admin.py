from django.contrib import admin

from scraper.models import TikTokVideo, TikTokUser, Hashtag, TikTokVideo_B, TikTokUser_B


@admin.register(TikTokVideo)
class TikTokVideoAdmin(admin.ModelAdmin):
    pass

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass

@admin.register(TikTokUser)
class TikTokUserAdmin(admin.ModelAdmin):
    pass

@admin.register(TikTokVideo_B)
class TikTokVideoBAdmin(admin.ModelAdmin):
    list_display = ('id', 'video_id', 'scrape_date')  # Add more fields if needed
    search_fields = ('video_id',)  # Enables search by `video_id`
    list_filter = ('scrape_date',)  # Adds filtering by date (if applicable)

@admin.register(TikTokUser_B)
class TikTokUserBAdmin(admin.ModelAdmin):
    pass
