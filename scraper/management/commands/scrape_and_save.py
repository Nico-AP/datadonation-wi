from django.core.management.base import BaseCommand

from scraper.scraper import get_tt_videos


class Command(BaseCommand):
    help = "Scrape data and store it in the database"

    def handle(self, *args, **options):
        # Run your scraping logic
        get_tt_videos()
