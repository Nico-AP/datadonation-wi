from django.core.management.base import BaseCommand
from reports.generate_public_plots import generate_public_plots
from reports.utils.data_processing import load_posts_data
from scraper.scraper import get_tt_videos


class Command(BaseCommand):
    help = "Scrape data and store it in the database"

    def handle(self, *args, **options):
        # Run your scraping logic
        get_tt_videos()
        
        # Generate and cache public plots
        df_posts = load_posts_data()
        generate_public_plots(df_posts)
