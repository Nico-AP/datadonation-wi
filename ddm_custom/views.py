from ddm.participation.views import BriefingView, DataDonationView


class BriefingViewCustom(BriefingView):
    step_name = 'briefing-ddm-custom'
    steps = [
        'briefing-ddm-custom',
        'data-donation-custom',
        'ddm_participation:questionnaire',
        'ddm_participation:debriefing'
    ]
    pass


class DataDonationViewCustom(DataDonationView):
    template_name = 'ddm_custom/custom_donation.html'
    step_name = 'data-donation-custom'
    steps = [
        'briefing-ddm-custom',
        'data-donation-custom',
        'ddm_participation:questionnaire',
        'ddm_participation:debriefing'
    ]
    pass
