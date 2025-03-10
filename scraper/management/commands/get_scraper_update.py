from django.db.models import Count, Q
from django.core.management.base import BaseCommand
from scraper.models import TikTokVideo_B, TikTokUser_B
from rich.console import Console


console = Console()

class Command(BaseCommand):
    help = 'Prints an overview of scraping progress.'

    def print_status(self, name, stats):
        console.print(f'[white bold]Scraping Progress {name}:[/]')
        console.print(f'[white]{name} in DB: {stats["total"]}')
        console.print(f'[white]Attempted: {stats["attempted"]}')
        console.print(f'[green]Successful: {stats["success"]}')
        if stats["total"] > 0:
            console.print(f'[pink]Scraped {stats["attempted"]/stats["total"]*100:.2f}% of {name}')
        console.print('--------------------------------------')

    def handle(self, *args, **options):
        # Get overview for TT videos.
        counts_videos = TikTokVideo_B.objects.aggregate(
            total=Count('id'),
            attempted=Count('id', filter=Q(scrape_date__isnull=False)),
            success=Count('id', filter=Q(scrape_success=True))
        )
        self.print_status('Videos', counts_videos)

        # Get overview for TT users.
        counts_users = TikTokUser_B.objects.aggregate(
            total=Count('id'),
            attempted=Count('id', filter=Q(scrape_date__isnull=False)),
            success=Count('id', filter=Q(scrape_success=True))
        )
        self.print_status('Users', counts_users)
