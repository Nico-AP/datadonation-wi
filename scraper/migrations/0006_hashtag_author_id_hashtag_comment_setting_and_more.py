# Generated by Django 4.2.19 on 2025-03-05 13:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("scraper", "0005_tiktokvideo_scrape_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="hashtag",
            name="author_id",
            field=models.BigIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="comment_setting",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="create_time",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="download_setting",
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="duet_setting",
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="ftc",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="is_ad_virtual",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="nick_name",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="open_favorite",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="private_account",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="recommend_reason",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="relation",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="secret",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="signature",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="stitch_setting",
            field=models.SmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="suggest_account_bind",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="hashtag",
            name="verified",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="TikTokVideo_B",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("video_id", models.BigIntegerField(unique=True)),
                ("video_description", models.TextField(blank=True, null=True)),
                ("create_time", models.DateTimeField()),
                ("comment_count", models.IntegerField(null=True)),
                ("like_count", models.IntegerField(null=True)),
                ("share_count", models.IntegerField(null=True)),
                ("view_count", models.IntegerField(null=True)),
                ("music_id", models.BigIntegerField(null=True)),
                ("region_code", models.CharField(max_length=255, null=True)),
                ("schedule_time", models.IntegerField(null=True)),
                ("is_ad", models.BooleanField(default=False)),
                ("suggested_words", models.CharField(max_length=255, null=True)),
                ("diggcount", models.IntegerField(null=True)),
                ("collectcount", models.IntegerField(null=True)),
                ("repostcount", models.IntegerField(null=True)),
                ("poi_name", models.CharField(max_length=255, null=True)),
                ("poi_address", models.CharField(max_length=255, null=True)),
                ("poi_city", models.CharField(max_length=255, null=True)),
                ("warn_info", models.JSONField(null=True)),
                ("original_item", models.BooleanField(default=False)),
                ("offical_item", models.BooleanField(default=False)),
                ("secret", models.BooleanField(default=False)),
                ("for_friend", models.BooleanField(default=False)),
                ("digged", models.BooleanField(default=False)),
                ("item_comment_status", models.SmallIntegerField(null=True)),
                ("take_down", models.IntegerField(null=True)),
                ("effect_stickers", models.CharField(max_length=255, null=True)),
                ("private_item", models.BooleanField(default=False)),
                ("duet_enabled", models.BooleanField(default=False)),
                ("stitch_enabled", models.BooleanField(default=False)),
                ("stickers_on_item", models.CharField(max_length=255, null=True)),
                ("share_enabled", models.BooleanField(default=False)),
                ("comments", models.CharField(max_length=255, null=True)),
                ("duet_display", models.IntegerField(null=True)),
                ("stitch_display", models.IntegerField(null=True)),
                ("index_enabled", models.BooleanField(default=False)),
                ("diversification_labels", models.CharField(max_length=255, null=True)),
                ("diversification_id", models.BigIntegerField(null=True)),
                ("channel_tags", models.CharField(max_length=255, null=True)),
                ("keyword_tags", models.CharField(max_length=255, null=True)),
                ("is_ai_gc", models.BooleanField(default=False)),
                ("ai_gc_description", models.TextField(null=True)),
                ("filepath", models.TextField(null=True)),
                ("duration", models.IntegerField(null=True)),
                ("height", models.IntegerField(null=True)),
                ("width", models.IntegerField(null=True)),
                ("ratio", models.IntegerField(null=True)),
                ("volume_loudness", models.FloatField(null=True)),
                ("volume_peak", models.FloatField(null=True)),
                ("has_original_audio", models.BooleanField(default=False)),
                ("enable_audio_caption", models.BooleanField(default=False)),
                ("no_caption_reason", models.SmallIntegerField(null=True)),
                (
                    "scrape_date",
                    models.DateTimeField(
                        default=datetime.datetime(
                            1999, 12, 31, 23, 0, tzinfo=datetime.timezone.utc
                        )
                    ),
                ),
                (
                    "hashtags",
                    models.ManyToManyField(
                        blank=True, related_name="tt_videos_b", to="scraper.hashtag"
                    ),
                ),
                (
                    "mentions",
                    models.ManyToManyField(
                        blank=True, related_name="tt_videos_b", to="scraper.tiktokuser"
                    ),
                ),
                (
                    "username",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="scraper.tiktokuser",
                    ),
                ),
            ],
        ),
    ]
