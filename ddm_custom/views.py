from ddm.participation.views import BriefingView, DataDonationView


class BriefingViewCustom(BriefingView):
    step_name = 'briefing-custom'
    steps = [
        'briefing-ddm-custom',
        'data-donation-custom',
        'questionnaire',
        'debriefing'
    ]
    pass


class DataDonationViewCustom(DataDonationView):
    template_name = 'ddm_custom/custom_donation.html'
    step_name = 'data-donation-custom'
    steps = [
        'briefing-ddm-custom',
        'data-donation-custom',
        'questionnaire',
        'debriefing'
    ]
    pass
