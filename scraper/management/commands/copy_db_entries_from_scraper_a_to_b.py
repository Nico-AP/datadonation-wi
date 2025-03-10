import itertools
import sys

from django.core.management.base import BaseCommand
from ddm.datadonation.models import DataDonation, DonationBlueprint
from rich.console import Console
from scraper.models import TikTokVideo_B, TikTokVideo
from tqdm import tqdm

console = Console()


def print_to_console(msg):
    sys.stdout.write('\033[F')  # Move cursor up to overwrite the last task message
    sys.stdout.write('\033[K')  # Clear the line
    console.print(msg, end='')
    sys.stdout.write('\033[E')  # Moves cursor down one line
    sys.stdout.flush()

class Command(BaseCommand):
    help = 'Copy videos from scraper A to scraper B.'

    def handle(self, *args, **options):
        console.print('[white]Start copying videos to scraper B.[/]')

        # Get all videos from scraper A
        video_ids = TikTokVideo.objects.all().order_by('pk').values_list('video_id', flat=True)
        self.bulk_insert_videos(video_ids)

        console.print('[bold green]✅ All entries added to db.[/]')
        return

    def bulk_insert_videos(self, video_ids):
        BATCH_SIZE = 1000

        # Prepare objects for bulk creation
        for i in range(0, len(video_ids), BATCH_SIZE):
            print_to_console(f'[yellow] Adding videos {i}:{i + BATCH_SIZE}.')
            ids_to_insert = video_ids[i:i + BATCH_SIZE]
            new_videos = [TikTokVideo_B(video_id=video_id) for video_id in ids_to_insert]
            TikTokVideo_B.objects.bulk_create(new_videos, ignore_conflicts=True)
