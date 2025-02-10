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
            choices=['all', 'day', 'past_day', 'accounts'],
            default='all',
            help='''Scraping mode:
                all (default) - Run complete scraping (past day + full account history)
                past_day - Scrape past day only (4 days ago)
                day - Scrape specific day (requires --date)
                accounts - Only update full account history
            '''
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

        try:
            if mode == 'all':
                self.stdout.write('Running complete scraping...')
                logger.info('Running complete scraping (new day + account updates)')
                get_tt_videos_new_day()
                get_tt_videos_update_account_data()
            
            elif mode == 'day':
                if not date:
                    self.stderr.write('Error: --date is required for day mode')
                    logger.error('No date provided for day mode')
                    return
                self.stdout.write(f'Scraping specific day: {date}')
                logger.info(f'Scraping specific day: {date}')
                get_tt_videos_new_day(specific_date=date)
            
            elif mode == 'past_day':
                past_date = get_formatted_date()  # Gets date 4 days ago by default
                self.stdout.write(f'Scraping past day (4 days ago): {past_date}')
                logger.info(f'Scraping past day: {past_date}')
                get_tt_videos_new_day()
            
            elif mode == 'accounts':
                self.stdout.write('Updating account data only...')
                logger.info('Running account data update only')
                get_tt_videos_update_account_data()

            logger.info('Scraping completed successfully')
            self.stdout.write(self.style.SUCCESS('Scraping completed successfully'))

            # Generate and cache public plots
            logger.info('Generating public plots...')
            df_posts = load_posts_data()
            generate_public_plots(df_posts)
            logger.info('Public plots generated and cached')

        except Exception as e:
            logger.error(f'Error during scraping: {str(e)}')
            self.stderr.write(self.style.ERROR(f'Scraping failed: {str(e)}'))
            raise

        logger.info('=' * 50)
