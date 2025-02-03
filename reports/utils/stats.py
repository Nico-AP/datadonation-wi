import pandas as pd

def create_stats_table(df):
    """
    Create a summary statistics table from the posts dataframe.
    
    Args:
        df (pd.DataFrame): DataFrame containing TikTok posts data
        
    Returns:
        pd.DataFrame: Summary statistics table
    """
    # Calculate basic statistics
    stats = {
        'Metric': [
            'Total Videos',
            'Average Likes',
            'Average Shares',
            'Average Comments',
            'Average Views'
        ],
        'Value': [
            len(df),
            df['like_count'].mean(),
            df['share_count'].mean(),
            df['comment_count'].mean(),
            df['view_count'].mean()
        ]
    }
    
    # Create DataFrame and round numeric values
    stats_df = pd.DataFrame(stats)
    stats_df['Value'] = stats_df['Value'].round(2)
    
    return stats_df 