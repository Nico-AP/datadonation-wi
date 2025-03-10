from django.db import models
from django.utils.timezone import make_aware
from datetime import datetime


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


class TikTokUser(models.Model):
    # name = username in TikTokUser_B
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name



class TikTokUser_B(models.Model):
    # name = username in TikTokUser
    username = models.CharField(max_length=255)
    ###### ADDED FIELDS ######
    author_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True)
    ## in TikTok_Content_Scraper scheme "name"
    nick_name = models.CharField(max_length=255, null=True, blank=True)
    signature = models.TextField(null=True, blank=True)
    create_time = models.IntegerField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    ftc = models.BooleanField(default=False)
    relation = models.IntegerField(null=True, blank=True)
    open_favorite = models.BooleanField(default=False)
    comment_setting = models.IntegerField(null=True, blank=True)
    duet_setting = models.SmallIntegerField(null=True, blank=True)
    stitch_setting = models.SmallIntegerField(null=True, blank=True)
    private_account = models.BooleanField(default=False)
    secret = models.BooleanField(default=False)
    is_ad_virtual = models.BooleanField(default=False)
    download_setting = models.SmallIntegerField(null=True, blank=True)
    recommend_reason = models.CharField(max_length=255, null=True, blank=True)
    suggest_account_bind = models.BooleanField(default=False)

    scrape_success = models.BooleanField(default=False)
    scrape_status = models.TextField(null=True)
    scrape_date = models.DateTimeField(
        null=True,
        blank=True,
        default=None
    )

    date_added = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )

    class Meta:
        verbose_name = "TikTok User (scraper B)"
        verbose_name_plural = "TikTok Users (scraper B)"

    def __str__(self):
        return str(self.author_id) if self.author_id else self.username



class TikTokVideo(models.Model):
    video_id = models.BigIntegerField(unique=True)
    video_description = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField()
    author_id = models.ForeignKey(
        TikTokUser,
        on_delete=models.SET_NULL,
        null=True
    )

    comment_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    share_count = models.IntegerField(null=True)
    view_count = models.IntegerField(null=True)

    hashtags = models.ManyToManyField(
        Hashtag,
        blank=True,
        related_name='tt_videos'
    )
    music_id = models.BigIntegerField(null=True)
    region_code = models.CharField(max_length=255, null=True)

    scrape_date = models.DateTimeField(
        default=make_aware(datetime(2000, 1, 1, 0, 0, 0))
    )

    def __str__(self):
        return str(self.video_id)


class TikTokVideo_B(models.Model):
    video_id = models.CharField(max_length=100, unique=True)
    video_description = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    author_id = models.ForeignKey(
        TikTokUser_B,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    comment_count = models.IntegerField(null=True, blank=True)
    like_count = models.IntegerField(null=True, blank=True)
    share_count = models.IntegerField(null=True, blank=True)
    view_count = models.IntegerField(null=True, blank=True)

    hashtags = models.ManyToManyField(
        Hashtag,
        blank=True,
        related_name='tt_videos_b'
    )
    music_id = models.BigIntegerField(null=True, blank=True)
    region_code = models.CharField(max_length=255, null=True, blank=True)

    ##### NEW METADATA FIELDS #####
    # new fields for table B
    mentions = models.ManyToManyField(
        TikTokUser_B,
        blank=True,
        related_name='mentions_b'
    )

    schedule_time = models.IntegerField(null=True, blank=True)
    is_ad = models.BooleanField(default=False)
    suggested_words = models.CharField(max_length=255, null=True, blank=True)
    diggcount = models.IntegerField(null=True, blank=True)
    collectcount = models.IntegerField(null=True, blank=True)
    repostcount = models.IntegerField(null=True, blank=True)
    poi_name = models.CharField(max_length=255, null=True, blank=True)
    poi_address = models.CharField(max_length=255, null=True, blank=True)
    poi_city = models.CharField(max_length=255, null=True, blank=True)
    warn_info = models.JSONField(null=True, blank=True)
    original_item = models.BooleanField(default=False)
    offical_item = models.BooleanField(default=False)
    secret = models.BooleanField(default=False)
    for_friend = models.BooleanField(default=False)
    digged = models.BooleanField(default=False)
    item_comment_status = models.SmallIntegerField(null=True, blank=True)
    take_down = models.IntegerField(null=True, blank=True)
    effect_stickers = models.JSONField(null=True, blank=True)  # Array of strings
    private_item = models.BooleanField(default=False)
    duet_enabled = models.BooleanField(default=False)
    stitch_enabled = models.BooleanField(default=False)
    stickers_on_item = models.JSONField(null=True, blank=True)  # Array of strings
    share_enabled = models.BooleanField(default=False)
    comments = models.JSONField(null=True, blank=True)  # Array of comment objects
    duet_display = models.IntegerField(null=True, blank=True)
    stitch_display = models.IntegerField(null=True, blank=True)
    index_enabled = models.BooleanField(default=False)
    diversification_labels = models.JSONField(null=True, blank=True)  # Array of strings
    diversification_id = models.BigIntegerField(null=True, blank=True)
    channel_tags = models.JSONField(null=True, blank=True)  # Array of strings
    keyword_tags = models.JSONField(null=True, blank=True)  # Array of strings
    is_ai_gc = models.BooleanField(default=False)
    ai_gc_description = models.TextField(null=True, blank=True)

    filepath = models.TextField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    ratio = models.IntegerField(null=True, blank=True)
    volume_loudness = models.FloatField(null=True, blank=True)
    volume_peak = models.FloatField(null=True, blank=True)
    has_original_audio = models.BooleanField(null=True, default=None, blank=True)
    enable_audio_caption = models.BooleanField(null=True, default=None, blank=True)
    no_caption_reason = models.SmallIntegerField(null=True, blank=True)

    scrape_success = models.BooleanField(default=False)
    scrape_status = models.TextField(null=True)
    scrape_date = models.DateTimeField(
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        verbose_name = "TikTok Video (scraper B)"
        verbose_name_plural = "TikTok Videos (scraper B)"

    def __str__(self):
        return str(self.video_id)
