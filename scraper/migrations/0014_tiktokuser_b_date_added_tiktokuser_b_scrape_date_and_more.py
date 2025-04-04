# Generated by Django 4.2.18 on 2025-03-07 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0013_alter_tiktokuser_b_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiktokuser_b',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tiktokuser_b',
            name='scrape_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='tiktokuser_b',
            name='scrape_status',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='tiktokuser_b',
            name='scrape_success',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tiktokvideo_b',
            name='scrape_status',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='tiktokvideo_b',
            name='scrape_success',
            field=models.BooleanField(default=False),
        ),
    ]
