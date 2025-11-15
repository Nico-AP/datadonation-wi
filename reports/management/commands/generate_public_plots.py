from django.core.management.base import BaseCommand
from reports.utils.data_processing import load_posts_data
from reports.generate_public_plots import generate_public_plots


class Command(BaseCommand):
    help = (
        'Generate and cache public plots using existing database data and '
        'keep in cache'
    )

    def handle(self, *args, **options):
        try:
            print("Loading posts data...")
            needed_fields = [
                'video_id',
                'create_time',
                'view_count',
                'author_id__name',
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
