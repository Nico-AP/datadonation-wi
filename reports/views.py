import pytz
from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from scraper.models import TikTokVideo

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
import pandas as pd

from .utils.data_processing import load_user_data, augment_posts_data
from .utils.plots import (
    create_user_consumption_stats,
    create_party_distribution_user_feed,
    create_temporal_party_distribution_user_feed,
    create_top_videos_table,
    create_user_feed_wordcloud,
    create_hashtag_cloud_germany
)
from .utils.utils import extract_video_id




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
        participant = self.get_participant()
        donated_data = self.get_donation(participant=participant)

        # Get all videos from the database
        videos = TikTokVideo.objects.all().values(
            'video_id',
            'create_time',
            'video_description',
            'view_count',
            'like_count',
            'comment_count',
            'share_count',
            'username__name',
            'hashtags__name'
        )
        
        df_posts = pd.DataFrame.from_records(videos)
        df_posts = df_posts.rename(columns={
            'username__name': 'username',
            'hashtags__name': 'hashtags'
        })
        
        #### fuse video with hashtag data - TODO: pack into load_posts_data_fucntion perhaps
        # Group hashtags by video_id since each video can have multiple hashtags
        df_hashtags = df_posts.groupby('video_id')['hashtags'].apply(list).reset_index()

        # Remove duplicates from video data (keeping first occurrence)
        df_posts = df_posts.drop('hashtags', axis=1).drop_duplicates(subset=['video_id'])

        # Merge hashtags back into main dataframe
        df_posts = df_posts.merge(df_hashtags, on='video_id', how='left')

        # Replace NaN with empty lists for videos without hashtags
        df_posts['hashtags'] = df_posts['hashtags'].apply(lambda x: [] if pd.isna(x).any() else x)


        #### Augment posts data - TODO: add simply "partei" col to database?
        df_posts = augment_posts_data(df_posts)
        # Parse donated data
        df_user_data = load_user_data(donated_data)

        #### conduct user feed matching to feed in user feed plots
        # Get watched video IDs and match with posts
        watched_video_ids = set(df_user_data['Link'].apply(extract_video_id))
        matched_videos = df_posts[df_posts['video_id'].isin(watched_video_ids)].copy()
        print(len(matched_videos))
        print(matched_videos.head())

        #### Plots feed related
        user_consumption_stats = create_user_consumption_stats(matched_videos, df_user_data)
        party_distribution_user_feed = create_party_distribution_user_feed(matched_videos)
        temporal_party_distribution_user_feed = create_temporal_party_distribution_user_feed(matched_videos)
        top_videos_table = create_top_videos_table(matched_videos)
        user_feed_wordcloud = create_user_feed_wordcloud(matched_videos)
        hashtag_cloud_germany = create_hashtag_cloud_germany(df_posts)

        context['user_consumption_stats'] = user_consumption_stats
        context['party_distribution_user_feed'] = party_distribution_user_feed
        context['temporal_party_distribution_user_feed'] = temporal_party_distribution_user_feed
        context['top_videos_table'] = top_videos_table
        context['user_feed_wordcloud'] = user_feed_wordcloud
        context['hashtag_cloud_germany'] = hashtag_cloud_germany
        
        return context

