import itertools
import sys
from datetime import datetime

from django.core.management.base import BaseCommand
from ddm.datadonation.models import DataDonation, DonationBlueprint
from django.utils import timezone
from rich.console import Console
from scraper.models import TikTokVideo_B
from tqdm import tqdm

console = Console()


def print_to_console(msg):
    sys.stdout.write('\033[F')  # Move cursor up to overwrite the last task message
    sys.stdout.write('\033[K')  # Clear the line
    console.print(msg, end='')
    sys.stdout.write('\033[E')  # Moves cursor down one line
    sys.stdout.flush()

class Command(BaseCommand):
    help = 'Extract video IDs from donations and add to database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bp_id',
            type=int,
            help='ID of the watched videos blueprint.'
        )
        parser.add_argument(
            '--max_donations',
            type=int,
            help='Number of donations to process.'
        )

    def handle(self, *args, **options):
        console.print('[white]Start populate_video_ids_to_db.[/]')

        # Get watched videos blueprint
        bp_id_watched_videos = options.get('bp_id')
        bp = DonationBlueprint.objects.get(pk=bp_id_watched_videos)

        # Get n donation to process.
        max_donations = options.get('max_donations')

        # Get project.
        self.project = bp.project

        print_to_console('[white]Get count of successful donations.')
        cutoff_date = datetime(2025, 2, 1, tzinfo=timezone.utc)
        total_count = DataDonation.objects.filter(
            blueprint=bp,
            consent=True,
            status='success',
            time_submitted__gt=cutoff_date
        ).count()

        print_to_console('[white]Get donation queryset iterator.')
        # Get donation belonging to watch history blueprint.
        donations_queryset = DataDonation.objects.filter(
            blueprint=bp,
            consent=True,
            status='success',
            time_submitted__gt=cutoff_date
        ).iterator(chunk_size=10)

        if max_donations:
            donations_queryset = itertools.islice(donations_queryset, max_donations)

        pbar = tqdm(total=total_count, dynamic_ncols=True, position=0, leave=True, colour="magenta")
        for donation in donations_queryset:
            participant_id = donation.participant.external_id
            video_ids = self.extract_video_ids(donation, participant_id)
            self.bulk_insert_videos(video_ids, participant_id)
            pbar.update(1)
        pbar.update(1)

        console.print('[bold green]✅ All entries updated in db.[/]')
        return

    def extract_video_ids(self, donation, participant_id):
        print_to_console(f'[cyan]Getting videos for {participant_id}.')
        data = donation.get_decrypted_data(
            self.project.secret, self.project.get_salt())

        video_ids_clean = {
            item['Link'].rstrip('/').split('/')[-1]
            for item in data
            if 'Link' in item and 'Date' in item
               and datetime.strptime(item['Date'], '%Y-%m-%d %H:%M:%S').year == 2025
        }
        return list(video_ids_clean)

    def bulk_insert_videos(self, video_ids, participant_id):
        BATCH_SIZE = 5000

        # Prepare objects for bulk creation
        for i in range(0, len(video_ids), BATCH_SIZE):
            print_to_console(f'[cyan]Processing {participant_id}: [yellow] Updating video ids {i}:{i + BATCH_SIZE}.')
            ids_to_update = video_ids[i:i + BATCH_SIZE]
            TikTokVideo_B.objects.filter(
                video_id__in=ids_to_update, scrape_priority=0).update(scrape_priority=1)
