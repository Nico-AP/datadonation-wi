from jinja2 import Environment, FileSystemLoader
from utils.data_processing import load_posts_data
from reports.utils.old_visualization import (
    create_user_consumption_stats,
    create_party_distribution_user_feed,
    create_temporal_party_distribution_user_feed,
    create_top_videos_table,
    create_user_feed_wordcloud,
    create_all_accounts_wordcloud,
    create_temporal_party_distribution_all_accounts,
    create_party_distribution_all_accounts,
    create_views_bars_all_accounts,
    create_likes_bars_all_accounts
)
import os

def main():
    # Create assets directory if it doesn't exist
    os.makedirs('./reports/assets', exist_ok=True)
    
    # Load data
    df_posts = load_posts_data(
        "./reports/data_temp/df_pol_videos.csv",
        "./reports/data_temp/df_actor_party.csv"
    )

    ### temp user data
    user_data_path = "./reports/data_temp/user_data_tiktok_2.json"
    
    # Create all visualizations

    #### 1. User consumption stats
    figure_1_user_consumption_stats = create_user_consumption_stats(df_posts, user_data_path)

    ### 2. Party distribution in user feed
    figure_2_party_distribution_user_feed = create_party_distribution_user_feed(df_posts, user_data_path)

    ### 3. Party distriubtion on feed temporal
    figure_3_temporal_party_distribution_user_feed = create_temporal_party_distribution_user_feed(df_posts, user_data_path)

    ### 4. Top videos table
    figure_4_top_videos_table = create_top_videos_table(df_posts, user_data_path)

    ### 5. User feed wordcloud
    figure_5_user_feed_wordcloud = create_user_feed_wordcloud(df_posts, user_data_path)

    ### 6. All accounts wordcloud
    figure_6_all_accounts_wordcloud = create_all_accounts_wordcloud(df_posts)

    ### 7. Party distribution all accounts temporal
    figure_7_temporal_party_distribution_all_accounts = create_temporal_party_distribution_all_accounts(df_posts)

    ### 8. Party distribution all accounts treemap
    figure_8_party_distribution_all_accounts = create_party_distribution_all_accounts(df_posts)

    ### 9. Views bar plots
    figure_9_views_bars_all_accounts = create_views_bars_all_accounts(df_posts)

    ### 10. Likes bar plots
    figure_10_likes_bars_all_accounts = create_likes_bars_all_accounts(df_posts)
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('./reports/templates/reports'))
    template = env.get_template('report_template_v3_sko.html')
    
    # Render template with HTML strings in the desired order
    rendered_html = template.render(
        consumption_stats=figure_1_user_consumption_stats,
        party_distribution=figure_2_party_distribution_user_feed['html']['party'],
        user_watched_videos=figure_3_temporal_party_distribution_user_feed['html'],
        top_videos_table=figure_4_top_videos_table,
        hashtag_cloud_user=figure_5_user_feed_wordcloud['html'],
        hashtag_cloud_germany=figure_6_all_accounts_wordcloud['html'],
        temporal_party=figure_7_temporal_party_distribution_all_accounts['html']['party'],
        video_count_treemap=figure_8_party_distribution_all_accounts['html'],
        video_count_treemap_top=figure_8_party_distribution_all_accounts['top_party'], #### double rendering to transport the top party info for correct text coloring
        views_bars=figure_9_views_bars_all_accounts['html'],
        views_bars_top=figure_9_views_bars_all_accounts['top_party'],
        likes_bars=figure_10_likes_bars_all_accounts['html'],
        likes_bars_top=figure_10_likes_bars_all_accounts['top_party']
    )
    
    # Save the HTML report
    with open('./report.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)

if __name__ == "__main__":
    main() 