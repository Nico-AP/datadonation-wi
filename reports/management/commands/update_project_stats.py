import os

from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from reports.models import ProjectStats

load_dotenv()


class Command(BaseCommand):
    help = "Scrape data and store it in the database"

    def handle(self, *args, **options):

        project_stats = ProjectStats.objects.get(public_key=os.getenv('REPORT_PROJECT_PK'))
        project_stats.update_stats()
