from django.core.management.base import BaseCommand
from scraper.scraper_B import (
    setup_logger,
    collect_metadata_for_all
)


class Command(BaseCommand):
    help = 'Scrape TikTok videos and save them to database'

    def add_arguments(self, parser):
        # Add optional arguments for different scraping modes
        parser.add_argument(
            '--mode',
            type=str,
            choices=['production', 'test'],
            default='production',
            help='''Scraping mode:
                production (default) - Run complete scraping (past day + full account history)
                test - Test mode: one request each for past day and account history
            '''
        )

    def handle(self, *args, **options):
        mode = options['mode']
        is_test = mode == 'test'

        # Setup single logger for entire session
        logger = setup_logger(f'command_{mode}')
        
        logger.info('=' * 50)
        logger.info(f'Starting scraping with mode: {mode}')
        if is_test:
            logger.info('TEST MODE: Will stop after first successful request')

        try:
            if mode == 'production':
                logger.info('Running complete scraping...')
                collect_metadata_for_all(logger=logger, test_mode=False)
            
            elif mode == 'test':
                logger.info('Running test mode...')
                collect_metadata_for_all(logger=logger, test_mode=True)
            
            logger.info('Scraping completed successfully')
            self.stdout.write(self.style.SUCCESS('Scraping completed successfully'))

        except Exception as e:
            logger.error(f'Error during scraping: {str(e)}')
            self.stderr.write(self.style.ERROR(f'Scraping failed: {str(e)}'))
            raise

        logger.info('=' * 50)