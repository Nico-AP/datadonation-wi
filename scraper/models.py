from django.db import models
from django.utils.timezone import make_aware
from datetime import datetime


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class TikTokUser(models.Model):
    name = models.CharField(max_length=255, unique=True)

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
