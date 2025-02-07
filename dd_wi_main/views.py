from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import TemplateView
from reports.utils.constants import (
    PUBLIC_TEMPORAL_PLOT_KEY,
    PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY,
    PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY,
    PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY
)


class LandingView(TemplateView):
    template_name = 'dd_wi_main/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get cached plots
        context['public_party_distribution_temporal_all_accounts'] = cache.get(PUBLIC_TEMPORAL_PLOT_KEY)
        context['public_party_distribution_all_accounts'] = cache.get(PUBLIC_PARTY_DISTRIBUTION_ALL_ACCOUNTS_KEY)
        context['public_views_bars_all_accounts'] = cache.get(PUBLIC_VIEWS_BARS_ALL_ACCOUNTS_KEY)
        context['public_likes_bars_all_accounts'] = cache.get(PUBLIC_LIKES_BARS_ALL_ACCOUNTS_KEY)

        return context


class WipView(TemplateView):
    """ Displays a work-in-progress page. """
    template_name = 'dd_wi_main/wip_page.html'


def custom_404_view(request, exception):
    """ Returns a custom 404 page. """
    return render(request, 'dd_wi_main/404.html', status=404)


def custom_500_view(request):
    """ Returns a custom 500 page. """
    return render(request, 'dd_wi_main/500.html', status=500)
