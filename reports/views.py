import pytz

from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from .utils.data_processing import load_user_data, load_posts_data
from .utils.plots import (
    create_party_distribution_user_feed,
    create_temporal_party_distribution_user_feed,
    create_top_videos_table,
    create_user_feed_wordcloud
)
from .utils.utils import extract_video_id
from .utils.constants import (
    PUBLIC_TEMPORAL_PLOT_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_HT_WORDCLOUD_KEY
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

    def add_feed_related_plots(self, context, df_matched_videos):
        """ Add feed-related plots to context. """
        context['party_distribution_user_feed'] = \
            create_party_distribution_user_feed(df_matched_videos)
        context['temporal_party_distribution_user_feed'] = \
            create_temporal_party_distribution_user_feed(df_matched_videos)
        context['top_videos_table'] = \
            create_top_videos_table(df_matched_videos)
        context['user_feed_wordcloud'] = \
            create_user_feed_wordcloud(df_matched_videos)
        return

    def add_static_public_plots(self, context):
        """ Add static public plots to context. """
        context['public_party_distribution_temporal_all_accounts'] = cache.get(
            PUBLIC_TEMPORAL_PLOT_KEY)
        context['public_party_distribution_all_accounts'] = cache.get(
            PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY)
        context['public_views_bars_all_accounts'] = cache.get(
            PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY)
        context['public_likes_bars_all_accounts'] = cache.get(
            PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY)
        context['hashtag_cloud_germany'] = cache.get(
            PUBLIC_HT_WORDCLOUD_KEY)
        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participant = self.get_participant()
        donated_data = self.get_donation(participant=participant)

        # Parse donated data and get list of watched video IDs.
        df_user_data = load_user_data(donated_data)
        watched_ids = list(set(df_user_data['Link'].apply(extract_video_id)))
        df_matched_videos = load_posts_data(video_ids=watched_ids)
        del watched_ids

        n_videos = len(df_user_data)
        n_matched = len(df_matched_videos)

        if n_videos == 0:
            share_political = 0
        else:
            share_political = round(n_matched / n_videos, 2) * 100

        if df_matched_videos is None or df_matched_videos.empty:
            matches = False
        else:
            matches = True
        context['matches'] = matches
        context['n_videos'] = n_videos
        context['n_matched'] = n_matched
        context['share_political'] = share_political

        # Plots feed related.
        if matches:
            self.add_feed_related_plots(context, df_matched_videos)

        # Add static plots based on public data to context.
        self.add_static_public_plots(context)
        return context
