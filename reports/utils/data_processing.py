import pandas as pd
import json
from scraper.models import TikTokVideo

def extract_username(url):
    """Extract username from TikTok URL"""
    try:
        # Split by @ and take the last part
        username = url.split('@')[-1]
        # Remove any trailing whitespace
        username = username.strip()
        return username
    except:
        return None

def load_csv_as_dict(csv_path):
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Convert to dictionary using first two columns
    # First column becomes keys, second column becomes values
    result_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    processed_dict = {extract_username(url): party for url, party in result_dict.items()}
    return processed_dict

def load_posts_data():
    """Load and process posts data"""
    account_dict = load_csv_as_dict('./reports/static/reports/csv/actor_party_mapping.csv')
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

    # Map accounts to parties, filling NaN values with "Kein offizieller Parteiaccount"
    df_posts['partei'] = df_posts['username'].map(account_dict).fillna("Kein offizieller Parteiaccount")

    
    return df_posts

def load_user_data(data_trace):
    # Process browsing history
    browsing_history = data_trace['Angesehene Videos']
    browsing_df = pd.DataFrame(browsing_history)
    browsing_df['Date'] = pd.to_datetime(browsing_df['Date'])
    
    return browsing_df 