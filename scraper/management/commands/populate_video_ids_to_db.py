import sys

from django.core.management.base import BaseCommand
from ddm.datadonation.models import DataDonation, DonationBlueprint
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

        # Get donation belonging to watch history blueprint.
        donations_queryset = DataDonation.objects.filter(
            blueprint=bp,
            consent=True,
            status='success'
        )

        if max_donations:
            donations_queryset = donations_queryset[:max_donations]

        total_count = donations_queryset.count()

        pbar = tqdm(total=total_count, dynamic_ncols=True, position=0, leave=True, colour="magenta")
        for donation in donations_queryset.iterator():
            self.extract_video_ids(donation)
            pbar.update(1)
        pbar.update(1)

        console.print('[bold green]✅ All entries added to db.[/]')
        return

    def extract_video_ids(self, donation):
        data = donation.get_decrypted_data(
            self.project.secret, self.project.get_salt())
        participant = donation.participant.external_id

        video_ids = [item["Link"].rstrip("/").split("/")[-1] for item in data]
        video_ids_clean = []
        for video_id in video_ids:
            try:
                int(video_id)
            except (ValueError, TypeError):
                print(f'{video_id}: Could not be converted to integer.')
                continue

            video_ids_clean.append(video_id)

        unique_video_ids = set(video_ids_clean)

        # Prepare objects for bulk creation
        new_videos = [TikTokVideo_B(video_id=video_id) for video_id in unique_video_ids]

        # Insert data in batches
        BATCH_SIZE = 10000
        for i in range(0, len(new_videos), BATCH_SIZE):
            print_to_console(f'[cyan]Processing {participant}: [yellow] Adding video ids {i}:{i + BATCH_SIZE}.')
            TikTokVideo_B.objects.bulk_create(new_videos[i:i + BATCH_SIZE], ignore_conflicts=True)
