import logging

import pandas as pd

from celery import shared_task
from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from .utils.data_processing import load_posts_data
from .utils.plots import (
    create_party_distribution_user_feed,
    create_temporal_party_distribution_user_feed,
    create_top_videos_table,
    create_user_feed_wordcloud
)
from .utils.utils import extract_video_id


logger = logging.getLogger(__name__)  # Get Celery's logger


def get_donation(participant_id, secret, salt):
    """
    Returns a dictionary with blueprint names as keys and the collected
    donations as values.
    """
    participant = Participant.objects.get(id=participant_id)
    data_donation = DataDonation.objects.filter(
        participant=participant,
        blueprint__name='Angesehene Videos'
    ).first()
    if data_donation is None:
        return None

    browsing_history = data_donation.get_decrypted_data(secret, salt)
    if browsing_history is None:
        return None

    browsing_df = pd.DataFrame(browsing_history)

    if browsing_df.empty or browsing_df is None:
        return None

    browsing_df['Date'] = pd.to_datetime(browsing_df['Date'], errors='coerce')
    start_date = pd.Timestamp('2025-01-01')
    browsing_df = browsing_df[browsing_df['Date'] >= start_date]
    return browsing_df


@shared_task
def generate_tiktok_report(participant_id, secret, salt):
    donated_data = get_donation(participant_id, secret, salt)

    result = {
        'no_watch_history': False,
        'matches': False,
    }

    if donated_data is None:
        result['no_watch_history'] = True
        return result

    watched_ids = list(set(donated_data['Link'].apply(extract_video_id)))
    df_matched_videos = load_posts_data(video_ids=watched_ids)

    n_videos = len(donated_data)
    n_matched = len(df_matched_videos)

    result['n_videos'] = n_videos
    result['n_matched'] = n_matched

    if n_videos > 0:
        result['share_political'] = round(n_matched / n_videos, 2) * 100
    else:
        result['share_political'] = 0

    if df_matched_videos is not None and not df_matched_videos.empty:
        result['matches'] = True
        result['plots'] = {
            'party_distribution_user_feed': create_party_distribution_user_feed(df_matched_videos),
            'temporal_party_distribution_user_feed': create_temporal_party_distribution_user_feed(df_matched_videos),
            'top_videos_table': create_top_videos_table(df_matched_videos),
            'user_feed_wordcloud': create_user_feed_wordcloud(df_matched_videos)
        }

    return result
