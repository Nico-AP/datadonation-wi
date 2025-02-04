import time

import pytz
from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
import pandas as pd

from .utils.data_processing import load_user_data, load_posts_data
from .utils.plots import (
    create_user_consumption_stats,
    create_party_distribution_user_feed,
    create_temporal_party_distribution_user_feed,
    create_top_videos_table,
    create_user_feed_wordcloud,
    create_hashtag_cloud_germany
)
from .utils.utils import extract_video_id
from .utils.constants import (
    PUBLIC_TEMPORAL_PLOT_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY
)




utc = pytz.UTC


class TikTokReport(TemplateView):
    template_name = 'reports/base.html'
    project_pk = settings.REPORT_PROJECT_PK

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = self.get_project()

    def get_project(self):
        return DonationProject.objects.filter(url_id=self.project_pk).first()

    def get_participant(self):
        """
        Returns the participant object. If no Participant object is found,
        returns a http 404 response.
        """
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participant, external_id=participant_id)

    def get_donation(self, participant):
        """
        Returns a dictionary with blueprint names as keys and the collected
        donations as values.
        """
        data_donations = DataDonation.objects.filter(participant=participant)
        donated_data = {}
        for data_donation in data_donations:
            bp_name = data_donation.blueprint.name
            donated_data[bp_name] = data_donation.get_decrypted_data(
                self.project.secret_key, self.project.get_salt())
        return donated_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_time = time.time()
        print(f'Start time: {start_time}')
        participant = self.get_participant()
        print(f'Time to participants: {time.time() - start_time}')
        donated_data = self.get_donation(participant=participant)
        print(f'Time to donations: {time.time() - start_time}')

        df_posts = load_posts_data()
        print(f'Time to df_posts: {time.time() - start_time}')
        
        # Parse donated data
        df_user_data = load_user_data(donated_data)
        print(f'Time to df_user_data: {time.time() - start_time}')

        #### conduct user feed matching to feed in user feed plots
        # Get watched video IDs and match with posts
        watched_video_ids = set(df_user_data['Link'].apply(extract_video_id))
        matched_videos = df_posts[df_posts['video_id'].isin(watched_video_ids)].copy()
        print(f'Time to matched videos: {time.time() - start_time}')
        # TODO: Handle case no matched videos.

        #### Plots feed related
        user_consumption_stats = create_user_consumption_stats(matched_videos, df_user_data)
        print(f'Time to user_consumption_stats: {time.time() - start_time}')
        party_distribution_user_feed = create_party_distribution_user_feed(matched_videos)
        print(f'Time to party_distribution_user_feed: {time.time() - start_time}')
        temporal_party_distribution_user_feed = create_temporal_party_distribution_user_feed(matched_videos)
        print(f'Time to temporal_party_distribution_user_feed: {time.time() - start_time}')
        top_videos_table = create_top_videos_table(matched_videos)
        print(f'Time to top_videos_table: {time.time() - start_time}')
        user_feed_wordcloud = create_user_feed_wordcloud(matched_videos)
        print(f'Time to user_feed_wordcloud: {time.time() - start_time}')
        hashtag_cloud_germany = create_hashtag_cloud_germany(df_posts)
        print(f'Time to hashtag_cloud_germany: {time.time() - start_time}')

        context['user_consumption_stats'] = user_consumption_stats
        context['party_distribution_user_feed'] = party_distribution_user_feed
        context['temporal_party_distribution_user_feed'] = temporal_party_distribution_user_feed
        context['top_videos_table'] = top_videos_table
        context['user_feed_wordcloud'] = user_feed_wordcloud
        context['hashtag_cloud_germany'] = hashtag_cloud_germany

        ### public stuff
        context['public_party_distribution_temporal_all_accounts'] = cache.get(PUBLIC_TEMPORAL_PLOT_KEY)
        context['public_party_distribution_all_accounts'] = cache.get(PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY)
        context['public_views_bars_all_accounts'] = cache.get(PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY)
        context['public_likes_bars_all_accounts'] = cache.get(PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY)
        print("Debug - cached plot:", bool(context['public_party_distribution_temporal_all_accounts']))
        
        return context

