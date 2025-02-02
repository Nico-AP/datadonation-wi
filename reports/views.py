import pytz
from ddm.datadonation.models import DataDonation
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

utc = pytz.UTC


class TikTokReport(TemplateView):
    template_name = 'reports/base.html'
    project_pk = settings.REPORT_PROJECT_PK

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = self.get_project()

    def get_project(self):
        return DonationProject.objects.filter(url_id=self.project_pk).first()

    def get_participant(self):
        """
        Returns the participant object. If no Participant object is found,
        returns a http 404 response.
        """
        participant_id = self.kwargs.get('participant_id')
        return get_object_or_404(Participant, external_id=participant_id)

    def get_donation(self, participant):
        """
        Returns a dictionary with blueprint names as keys and the collected
        donations as values.
        """
        data_donations = DataDonation.objects.filter(participant=participant)
        donated_data = {}
        for data_donation in data_donations:
            bp_name = data_donation.blueprint.name
            donated_data[bp_name] = data_donation.get_decrypted_data(
                self.project.secret_key, self.project.get_salt())
        return donated_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participant = self.get_participant()
        donated_data = self.get_donation(participant=participant)
        context['donation'] = donated_data
        return context
