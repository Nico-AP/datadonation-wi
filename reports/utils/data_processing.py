import pandas as pd
from scraper.models import TikTokVideo


def extract_username(url):
    """ Extract username from TikTok URL. """
    try:
        # Split by @ and take the last part.
        username = url.split('@')[-1]
        # Remove any trailing whitespace.
        username = username.strip()
        return username
    except Exception:
        return None


def load_csv_as_dict(csv_path):
    df = pd.read_csv(csv_path)

    # Convert to dictionary using first two columns.
    # First column becomes keys, second column becomes values.
    result_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    processed_dict = {
        extract_username(url): party
        for url, party
        in result_dict.items()
    }
    return processed_dict


def load_posts_data(needed_fields=None, video_ids=None):
    """ Load and process posts data. """
    csv_path = './reports/static/reports/csv/actor_party_mapping.csv'
    account_dict = load_csv_as_dict(csv_path)

    # Get all videos from the database.
    if needed_fields is None:
        fields = [
            'video_id',
            'create_time',
            'view_count',
            'like_count',
            'username__name',
            'hashtags__name'
        ]
    else:
        fields = needed_fields

    if video_ids is None:
        videos = TikTokVideo.objects.all().values(*fields)
    else:
        videos = TikTokVideo.objects.none()
        BATCH_SIZE = 5000
        for i in range(0, len(video_ids), BATCH_SIZE):
            batch = video_ids[i:(i + BATCH_SIZE)]
            videos = videos | \
                TikTokVideo.objects.filter(video_id__in=batch).values(*fields)

    df_posts = pd.DataFrame.from_records(videos)
    df_posts = df_posts.rename(columns={
        'username__name': 'username',
        'hashtags__name': 'hashtags'
    })

    # Account for cases where no videos matched.
    if df_posts is None or df_posts.empty:
        return df_posts

    # Fuse video with hashtag data.
    # Group hashtags by video_id since each video can have multiple hashtags.
    df_hashtags = df_posts.groupby('video_id')
    df_hashtags = df_hashtags['hashtags'].apply(list).reset_index()

    # Remove duplicates from video data (keeping first occurrence).
    df_posts.drop('hashtags', axis=1, inplace=True)
    df_posts.drop_duplicates(subset=['video_id'], inplace=True)

    # Merge hashtags back into main dataframe.
    df_posts = df_posts.merge(df_hashtags, on='video_id', how='left')
    del df_hashtags

    # Replace NaN with empty lists for videos without hashtags.
    df_posts['hashtags'] = df_posts['hashtags'].apply(
        lambda x: [] if pd.isna(x).any() else x)

    # Map accounts to parties, filling NaN values with
    # "Kein offizieller Parteiaccount".
    df_posts['partei'] = df_posts['username'].map(account_dict).fillna(
        'Kein Parteiaccount')

    return df_posts


def load_user_data(data_traces):
    # Process browsing history.
    browsing_history = data_traces.get('Angesehene Videos')
    if browsing_history is None:
        return None
    browsing_df = pd.DataFrame(browsing_history)
    browsing_df['Date'] = pd.to_datetime(browsing_df['Date'])
    
    # Filter for videos watched after January 1st, 2025
    start_date = pd.Timestamp('2025-01-01')
    browsing_df = browsing_df[browsing_df['Date'] >= start_date]

    return browsing_df
