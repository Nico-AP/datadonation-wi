import pandas as pd
import json

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

def augment_posts_data(df_posts):
    """Load and process posts data"""
    # Load data
    account_dict = load_csv_as_dict('./reports/static/reports/csv/actor_party_mapping.csv')

    # Map accounts to parties, filling NaN values with "Kein offizieller Parteiaccount"
    df_posts['partei'] = df_posts['username'].map(account_dict).fillna("Kein offizieller Parteiaccount")
    
    return df_posts

def load_user_data(data_trace):
    # Process browsing history
    browsing_history = data_trace['Angesehene Videos']
    browsing_df = pd.DataFrame(browsing_history)
    browsing_df['Date'] = pd.to_datetime(browsing_df['Date'])
    
    return browsing_df 