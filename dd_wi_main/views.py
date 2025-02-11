from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import TemplateView
from reports.utils.constants import PUBLIC_TEMPORAL_PLOT_DARK_KEY


class LandingView(TemplateView):
    template_name = 'dd_wi_main/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get cached distribution plot.
        context['party_distribution_plot'] = cache.get(
            PUBLIC_TEMPORAL_PLOT_DARK_KEY)
        return context


class WipView(TemplateView):
    """ Displays a work-in-progress page. """
    template_name = 'dd_wi_main/wip_page.html'


class ContactView(TemplateView):
    """ Displays the contact page. """
    template_name = 'dd_wi_main/imprint.html'


class ImprintView(TemplateView):
    """ Displays the imprint page. """
    template_name = 'dd_wi_main/imprint.html'


class DataProtectionView(TemplateView):
    """ Displays the data protection page. """
    template_name = 'dd_wi_main/data_protection.html'


def custom_404_view(request, exception):
    """ Returns a custom 404 page. """
    return render(request, 'dd_wi_main/404.html', status=404)


def custom_500_view(request):
    """ Returns a custom 500 page. """
    return render(request, 'dd_wi_main/500.html', status=500)
