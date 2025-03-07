from django.core.management.base import BaseCommand
from ddm.datadonation.models import DataDonation, DonationBlueprint

from scraper.models import TikTokVideo_B


class Command(BaseCommand):
    help = 'Extract video IDs from donations and add to database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bp_id',
            type=int,
            help='ID of the watched videos blueprint.'
        )

    def handle(self, *args, **options):
        # Get watched videos blueprint
        bp_id_watched_videos = options.get('bp_id')
        bp = DonationBlueprint.objects.get(pk=bp_id_watched_videos)

        # Get project.
        self.project = bp.project

        # Get donation belonging to watch history blueprint.
        donations = DataDonation.objects.filter(
            blueprint=bp,
            consent=True,
            status='success'
        )
        i = 0
        for donation in donations:
            self.extract_video_ids(donation)
            i += 1
            print(f'{i}/{donations.count()} donations processed.')

        print('Done')
        return

    def extract_video_ids(self, donation):
        data = donation.get_decrypted_data(
            self.project.secret, self.project.get_salt())

        video_ids = [item["Link"].rstrip("/").split("/")[-1] for item in data]
        video_ids_clean = []
        for video_id in video_ids:
            try:
                int_value = int(video_id)
            except (ValueError, TypeError):
                print(f'{video_id}: Could not be converted to integer.')
                continue

            if -9223372036854775808 <= int_value <= 9223372036854775807:
                video_ids_clean.append(video_id)
            else:
                print(f'{video_id}: Exceeds bigint constraint.')
                continue

        unique_video_ids = set(video_ids_clean)

        # Prepare objects for bulk creation
        new_videos = [TikTokVideo_B(video_id=video_id) for video_id in unique_video_ids]

        # Insert data in batches
        BATCH_SIZE = 10000
        for i in range(0, len(new_videos), BATCH_SIZE):
            TikTokVideo_B.objects.bulk_create(new_videos[i:i + BATCH_SIZE], ignore_conflicts=True)
