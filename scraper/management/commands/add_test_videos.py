from django.core.management.base import BaseCommand
from scraper.models import TikTokVideo_B
from django.utils.timezone import make_aware
from datetime import datetime

###### just for local testing!
class Command(BaseCommand):
    help = 'Adds test video IDs to the database'

    def handle(self, *args, **options):
        # Test video IDs
        test_video_ids = [
            7398323154424171806,
            7447600730267061526,
            7445371706207669526,
            7445371712307669526,
            7297793475267857696,
            7273494772780715297,
            7307913591867460896,
            7283463780716023082,
            7297614619261095211,
            7297169323703979296,
            7297208699830193454,
            7277673705394900270,
            7279705821154495745,
        ]

        # Add test videos with minimal data
        for video_id in test_video_ids:
            video, created = TikTokVideo_B.objects.get_or_create(
                video_id=video_id,
                defaults={
                    'video_description': None,
                    'create_time': None,
                    'author_id': None,
                    'comment_count': None,
                    'like_count': None,
                    'share_count': None,
                    'view_count': None,
                    'music_id': None,
                    'region_code': None,
                    'scrape_date': None
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created test video: {video_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'Video already exists: {video_id}')) 