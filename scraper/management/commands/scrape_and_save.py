from django.core.management.base import BaseCommand
from reports.generate_public_plots import generate_public_plots
from reports.utils.data_processing import load_posts_data
from scraper.scraper import (
    get_tt_videos_new_day,
    get_tt_videos_update_account_data,
    get_formatted_date,
    logger
)


class Command(BaseCommand):
    help = 'Scrape TikTok videos and save them to database'

    def add_arguments(self, parser):
        # Add optional arguments for different scraping modes
        parser.add_argument(
            '--mode',
            type=str,
            choices=['all', 'day', 'accounts'],
            default='all',
            help='Scraping mode: all (default), day (specific day), or accounts (only account updates)'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to scrape in YYYYMMDD format (only used with --mode=day)'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        date = options.get('date')

        logger.info('=' * 50)
        logger.info(f'Starting scraping with mode: {mode}')
        if date:
            logger.info(f'Target date: {date}')

        if mode == 'all':
            self.stdout.write('Running complete scraping...')
            logger.info('Running complete scraping (new day + account updates)')
            get_tt_videos_new_day()
            get_tt_videos_update_account_data()
        
        elif mode == 'day':
            if not date:
                date = get_formatted_date()  # Use today's date if none specified
            self.stdout.write(f'Scraping specific day: {date}')
            logger.info(f'Scraping specific day: {date}')
            get_tt_videos_new_day(specific_date=date)
        
        elif mode == 'accounts':
            self.stdout.write('Updating account data only...')
            logger.info('Running account data update only')
            get_tt_videos_update_account_data()

        logger.info('Scraping completed successfully')
        logger.info('=' * 50)
        self.stdout.write(self.style.SUCCESS('Scraping completed successfully'))

        # Generate and cache public plots
        logger.info('Generating public plots...')
        df_posts = load_posts_data()
        generate_public_plots(df_posts)
        logger.info('Public plots generated and cached')
