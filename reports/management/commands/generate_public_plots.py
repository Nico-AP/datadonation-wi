from django.core.cache import cache
from django.core.management.base import BaseCommand
from reports.utils.data_processing import load_posts_data
from reports.generate_public_plots import generate_public_plots


class Command(BaseCommand):
    help = 'Generate and cache public plots using existing database data'

    def handle(self, *args, **options):
        try:
            # Test cache
            cache.set('test_key', 'test_value', 86400)
            test_value = cache.get('test_key')
            print("Debug - Cache test:", test_value == 'test_value')

            print("Loading posts data...")
            needed_fields = [
                'video_id',
                'create_time',
                'view_count',
                'username__name',
                'hashtags__name',
                'like_count',
                'comment_count',
                'share_count',
            ]
            df_posts = load_posts_data(needed_fields)

            print("Generating public plots...")
            generate_public_plots(df_posts)

            print("Successfully generated and cached public plots!")

        except Exception as e:
            print(f"Error generating plots: {str(e)}")
