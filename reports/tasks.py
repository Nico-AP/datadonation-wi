from celery import shared_task
from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from .utils.data_processing import load_user_data, load_posts_data
from .utils.plots import (
    create_party_distribution_user_feed,
    create_temporal_party_distribution_user_feed,
    create_top_videos_table,
    create_user_feed_wordcloud
)
from .utils.utils import extract_video_id


def get_donation(participant_id, secret, salt):
    """
    Returns a dictionary with blueprint names as keys and the collected
    donations as values.
    """
    participant = Participant.objects.get(id=participant_id)
    data_donations = DataDonation.objects.filter(participant=participant)
    donated_data = {}
    for data_donation in data_donations:
        if data_donation.blueprint is None:
            continue
        bp_name = data_donation.blueprint.name
        donated_data[bp_name] = data_donation.get_decrypted_data(
            secret, salt)
    return donated_data


@shared_task
def generate_tiktok_report(participant_id, secret, salt):
    donated_data = get_donation(participant_id, secret, salt)

    result = {
        'no_watch_history': False,
        'matches': False,
    }

    df_user_data = load_user_data(donated_data)
    if df_user_data is None:
        result['no_watch_history'] = True
        return result

    watched_ids = list(set(df_user_data['Link'].apply(extract_video_id)))
    df_matched_videos = load_posts_data(video_ids=watched_ids)

    n_videos = len(df_user_data)
    n_matched = len(df_matched_videos)

    result['n_videos'] = n_videos
    result['n_matched'] = n_matched
    result['share_political'] = round(n_matched / n_videos, 2) * 100 if n_videos > 0 else 0

    if df_matched_videos is not None and not df_matched_videos.empty:
        result['matches'] = True
        result['plots'] = {
            'party_distribution_user_feed': create_party_distribution_user_feed(df_matched_videos),
            'temporal_party_distribution_user_feed': create_temporal_party_distribution_user_feed(df_matched_videos),
            'top_videos_table': create_top_videos_table(df_matched_videos),
            'user_feed_wordcloud': create_user_feed_wordcloud(df_matched_videos)
        }

    return result
