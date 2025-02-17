from django.core.management.base import BaseCommand
from reports.generate_public_plots import generate_public_plots
from reports.utils.data_processing import load_posts_data
from scraper.scraper import (
    get_tt_videos_new_day,
    get_tt_videos_update_account_data,
    get_formatted_date,
    setup_logger
)


class Command(BaseCommand):
    help = 'Scrape TikTok videos and save them to database'

    def add_arguments(self, parser):
        # Add optional arguments for different scraping modes
        parser.add_argument(
            '--mode',
            type=str,
            choices=['all', 'day', 'past_day', 'accounts', 'all_test'],
            default='all',
            help='''Scraping mode:
                all (default) - Run complete scraping (past day + full account history)
                past_day - Scrape past day only (4 days ago)
                day - Scrape specific day (requires --date)
                accounts - Only update full account history
                all_test - Test mode: one request each for past day and account history
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
        is_test = mode == 'all_test'

        # Setup single logger for entire session
        logger = setup_logger(f'command_{mode}')
        
        logger.info('=' * 50)
        logger.info(f'Starting scraping with mode: {mode}')
        if is_test:
            logger.info('TEST MODE: Will stop after first successful request')
        if date:
            logger.info(f'Target date: {date}')

        try:
            if mode in ['all', 'all_test']:
                logger.info('Running complete scraping...')
                get_tt_videos_new_day(logger=logger, test_mode=is_test)
                get_tt_videos_update_account_data(logger=logger, test_mode=is_test)
            
            elif mode == 'day':
                if not date:
                    logger.error('No date provided for day mode')
                    return
                logger.info(f'Scraping specific day: {date}')
                get_tt_videos_new_day(specific_date=date, logger=logger)
            
            elif mode == 'past_day':
                past_date = get_formatted_date()
                logger.info(f'Scraping past day (4 days ago): {past_date}')
                get_tt_videos_new_day(logger=logger)
            
            elif mode == 'accounts':
                logger.info('Updating account data only...')
                get_tt_videos_update_account_data(logger=logger)

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
