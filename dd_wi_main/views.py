from django.core.cache import cache
from django.views.generic import TemplateView
from reports.utils.constants import PUBLIC_TEMPORAL_PLOT_KEY


class LandingView(TemplateView):
    template_name = 'dd_wi_main/landing_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debug'] = True  # Enable debug output
        
        # Test cache persistence
        cache.set('test_view_key', 'test_view_value', 86400)
        test_value = cache.get('test_view_key')
        print("Debug - View cache test:", test_value == 'test_view_value')
        
        # Get cached plots
        cached_plot = cache.get(PUBLIC_TEMPORAL_PLOT_KEY)
        if cached_plot:
            print("Debug - Landing: Found cached plot with keys:", cached_plot.keys())
            print("Debug - Landing: Plot HTML exists:", bool(cached_plot.get('html')))
            print("Debug - Landing: Plot HTML party exists:", bool(cached_plot.get('html', {}).get('party')))
        else:
            print("Debug - Landing: No cached plot found")
            # Try setting and getting immediately to test cache
            cache.set('test_plot', {'test': 'value'}, 86400)
            test_plot = cache.get('test_plot')
            print("Debug - Immediate cache test:", bool(test_plot))
        
        context['public_party_distribution_temporal_all_accounts'] = cached_plot
        
        return context
