from django.db import models
from django.utils.timezone import make_aware
from datetime import datetime


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


class TikTokUser(models.Model):
    name = models.CharField(max_length=255, unique=True)

    ###### ADDED FIELDS ######
    ## id --> bigint
    author_id = models.BigIntegerField(null=True)
    ## name --> character varying(250), in quentins scheme "name" - for us name is the "unique username"
    nick_name = models.CharField(max_length=255, null=True)
    ## signature --> text
    signature = models.TextField(null=True)
    ## create_time --> integer
    create_time = models.IntegerField(null=True)
    ## verified --> boolean
    verified = models.BooleanField(default=False)
    ## ftc --> boolean
    ftc = models.BooleanField(default=False)
    ## relation --> integer
    relation = models.IntegerField(null=True)
    ## open_favorite --> boolean
    open_favorite = models.BooleanField(default=False)
    ## comment_setting --> integer
    comment_setting = models.IntegerField(null=True)
    ## duet_setting --> smallint
    duet_setting = models.SmallIntegerField(null=True)
    ## stitch_setting --> smallint
    stitch_setting = models.SmallIntegerField(null=True)
    ## private_account --> boolean
    private_account = models.BooleanField(default=False)
    ## secret --> boolean
    secret = models.BooleanField(default=False)
    ## is_ad_virtual --> boolean
    is_ad_virtual = models.BooleanField(default=False)
    ## download_setting --> smallint
    download_setting = models.SmallIntegerField(null=True)
    ## recommend_reason --> character varying(250)
    recommend_reason = models.CharField(max_length=255, null=True)
    ## suggest_account_bind --> boolean
    suggest_account_bind = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TikTokVideo(models.Model):
    video_id = models.BigIntegerField(unique=True)
    video_description = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField()
    username = models.ForeignKey(
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
    video_id = models.BigIntegerField(unique=True)
    video_description = models.TextField(null=True, blank=True)
    create_time = models.DateTimeField(null=True)
    username = models.ForeignKey(
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
        related_name='tt_videos_b'
    )
    music_id = models.BigIntegerField(null=True)
    region_code = models.CharField(max_length=255, null=True)

    ##### NEW METADATA FIELDS #####
    # new fields for table B
    mentions = models.ManyToManyField(
        TikTokUser,
        blank=True,
        related_name='mentions_b'
    )

    schedule_time = models.IntegerField(null=True)
    is_ad = models.BooleanField(default=False)
    suggested_words = models.CharField(max_length=255, null=True)
    diggcount = models.IntegerField(null=True)
    collectcount = models.IntegerField(null=True)
    repostcount = models.IntegerField(null=True)
    poi_name = models.CharField(max_length=255, null=True)
    poi_address = models.CharField(max_length=255, null=True)
    poi_city = models.CharField(max_length=255, null=True)
    warn_info = models.JSONField(null=True)
    original_item = models.BooleanField(default=False)
    offical_item = models.BooleanField(default=False)
    secret = models.BooleanField(default=False)
    for_friend = models.BooleanField(default=False)
    digged = models.BooleanField(default=False)
    item_comment_status = models.SmallIntegerField(null=True)
    take_down = models.IntegerField(null=True)
    effect_stickers = models.JSONField(null=True)  # Array of strings
    private_item = models.BooleanField(default=False)
    duet_enabled = models.BooleanField(default=False)
    stitch_enabled = models.BooleanField(default=False)
    stickers_on_item = models.JSONField(null=True)  # Array of strings
    share_enabled = models.BooleanField(default=False)
    comments = models.JSONField(null=True)  # Array of comment objects
    duet_display = models.IntegerField(null=True)
    stitch_display = models.IntegerField(null=True)
    index_enabled = models.BooleanField(default=False)
    diversification_labels = models.JSONField(null=True)  # Array of strings
    diversification_id = models.BigIntegerField(null=True)
    channel_tags = models.JSONField(null=True)  # Array of strings
    keyword_tags = models.JSONField(null=True)  # Array of strings
    is_ai_gc = models.BooleanField(default=False)
    ai_gc_description = models.TextField(null=True)

    filepath = models.TextField(null=True)
    duration = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    ratio = models.IntegerField(null=True)
    volume_loudness = models.FloatField(null=True)
    volume_peak = models.FloatField(null=True)
    has_original_audio = models.BooleanField(default=False)
    enable_audio_caption = models.BooleanField(default=False)
    no_caption_reason = models.SmallIntegerField(null=True)

    scrape_date = models.DateTimeField(
        default=make_aware(datetime(2000, 1, 1, 0, 0, 0))
    )

    def __str__(self):
        return str(self.video_id)
