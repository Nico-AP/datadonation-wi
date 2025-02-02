from django.db import models


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
    username = models.ForeignKey(TikTokUser, on_delete=models.SET_NULL, null=True)

    comment_count = models.IntegerField()
    like_count = models.IntegerField()
    share_count = models.IntegerField()
    view_count = models.IntegerField()

    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='tt_videos')
    music_id = models.BigIntegerField()
    region_code = models.CharField(max_length=255)

    def __str__(self):
        return str(self.video_id)
