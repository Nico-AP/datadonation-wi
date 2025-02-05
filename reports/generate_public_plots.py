from django.core.cache import get_cache
from .utils.plots import (
    create_temporal_party_distribution_all_accounts,
    create_party_distribution_all_accounts,
    create_views_bars_all_accounts,
    create_likes_bars_all_accounts
)
from .utils.constants import (
    PUBLIC_TEMPORAL_PLOT_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY
)

CACHE_TIMEOUT = 86400  # 24 hours in seconds
PLOT_CACHE = get_cache('plots')


def generate_public_plots(df_posts):
    """ Generate plots for public display and cache them. """

    # Generate plots for all accounts (not user-specific)
    party_distribution_temporal = \
        create_temporal_party_distribution_all_accounts(df_posts)
    party_distribution_all_accounts = \
        create_party_distribution_all_accounts(df_posts)
    views_bars_all_accounts = \
        create_views_bars_all_accounts(df_posts)
    likes_bars_all_accounts = \
        create_likes_bars_all_accounts(df_posts)

    # Cache the results
    PLOT_CACHE.set(PUBLIC_TEMPORAL_PLOT_KEY,
                   party_distribution_temporal, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
                   party_distribution_all_accounts, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
                   views_bars_all_accounts, CACHE_TIMEOUT)
    PLOT_CACHE.set(PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY,
                   likes_bars_all_accounts, CACHE_TIMEOUT)
