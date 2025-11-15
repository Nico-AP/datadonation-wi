from django.core.cache import caches
from .utils.plots import (
    create_temporal_party_distribution_all_accounts,
    create_party_distribution_all_accounts,
    create_views_bars_all_accounts,
    create_likes_bars_all_accounts,
    create_hashtag_cloud_germany,
    create_temporal_party_distribution_all_accounts_dark,
    create_party_distribution_all_accounts_dark,
    create_views_bars_all_accounts_dark,
    create_likes_bars_all_accounts_dark,
    create_hashtag_cloud_germany_dark
)
from .utils.constants import (
    PUBLIC_TEMPORAL_PLOT_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_HT_WORDCLOUD_KEY,
    PUBLIC_TEMPORAL_PLOT_DARK_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_DARK_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_DARK_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_DARK_KEY,
    PUBLIC_HT_WORDCLOUD_DARK_KEY
)

CACHE_TIMEOUT = 86400  # 24 hours in seconds
PLOT_CACHE = caches['default']


def generate_public_plots(df_posts):
    """ Generate plots for public display and cache them. """

    # Generate plots for all accounts (not user-specific)
    party_distribution_temporal = \
        create_temporal_party_distribution_all_accounts(df_posts)
    party_distribution_temporal_dark = \
        create_temporal_party_distribution_all_accounts_dark(df_posts)
    party_distribution_all_accounts = \
        create_party_distribution_all_accounts(df_posts)
    party_distribution_all_accounts_dark = \
        create_party_distribution_all_accounts_dark(df_posts)
    views_bars_all_accounts = \
        create_views_bars_all_accounts(df_posts)
    views_bars_all_accounts_dark = \
        create_views_bars_all_accounts_dark(df_posts)
    likes_bars_all_accounts = \
        create_likes_bars_all_accounts(df_posts)
    likes_bars_all_accounts_dark = \
        create_likes_bars_all_accounts_dark(df_posts)
    ht_wordcloud = create_hashtag_cloud_germany(df_posts)
    ht_wordcloud_dark = create_hashtag_cloud_germany_dark(df_posts)

    # Cache the results
    PLOT_CACHE.set(PUBLIC_TEMPORAL_PLOT_KEY,
                   party_distribution_temporal, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_TEMPORAL_PLOT_DARK_KEY,
                   party_distribution_temporal_dark, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
                   party_distribution_all_accounts, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_DARK_KEY,
                   party_distribution_all_accounts_dark, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
                   views_bars_all_accounts, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_DARK_KEY,
                   views_bars_all_accounts_dark, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY,
                   likes_bars_all_accounts, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_LIKES_BARS_ALL_ACCOUNTS_DARK_KEY,
                   likes_bars_all_accounts_dark, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_HT_WORDCLOUD_KEY, ht_wordcloud, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_HT_WORDCLOUD_DARK_KEY, ht_wordcloud_dark, CACHE_TIMEOUT)
