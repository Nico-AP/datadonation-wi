from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = 'dd_wi_main/landing_page.html'
