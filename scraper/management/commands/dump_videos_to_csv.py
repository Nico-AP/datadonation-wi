from datetime import datetime

import csv
import os
from django.core.management import BaseCommand
from django.db.models.fields.related import ManyToManyField
from django.core.serializers.json import DjangoJSONEncoder

from scraper.models import TikTokVideo_B


def export_tiktok_videos_to_csv(queryset, output_path, chunk_size=10000):
    if not queryset.exists():
        print("No data to export.")
        return

    # Get all model field names except ManyToMany (handled separately).
    model = queryset.model
    field_names = [f.name for f in model._meta.get_fields()
                   if not isinstance(f, ManyToManyField)]

    # Add custom extra fields.
    extra_fields = [
        'author_username',
        'author_author_id',
        'hashtags',
        'mentions'
    ]

    all_fieldnames = field_names + extra_fields

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)
        writer.writeheader()

        total_exported = 0
        for start in range(0, queryset.count(), chunk_size):
            print(f'Exporting entries {start} to {start + chunk_size}.')
            chunk = queryset.order_by('id')[start:start + chunk_size].select_related(
                'author_id').prefetch_related('hashtags', 'mentions')

            for obj in chunk.iterator():
                row = {}

                for field in field_names:
                    value = getattr(obj, field)

                    # Convert datetime to ISO format
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()

                    # Convert JSON/dict types to string
                    elif isinstance(value, (dict, list)):
                        value = DjangoJSONEncoder().encode(value)

                    row[field] = value

                # Add related author info
                author = obj.author_id
                row['author_username'] = author.username if author else ''
                row['author_author_id'] = author.author_id if author else ''

                # Add hashtags (comma-separated)
                row['hashtags'] = ','.join(ht.name for ht in obj.hashtags.all())

                # Add mentions (list of tuples)
                row['mentions'] = str([
                    (mention.author_id, mention.username)
                    for mention in obj.mentions.all()
                ])

                writer.writerow(row)
                total_exported += 1

    print(f"Exported {total_exported} records to {output_path}")


class Command(BaseCommand):
    help = ('Create a csv-dump of all TikTokVideo_B instances that have been '
            '(attempted to be) scraped and save it to a "./dumps" folder.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--chunk_size',
            type=int,
            default=1000,
            help='Chunk size for DB iteration.'
        )

    def handle(self, *args, **options):
        videos = TikTokVideo_B.objects.filter(scrape_date__isnull=False)

        timestamp = datetime.now().isoformat().replace(":", "").replace(".", "")
        output_path = f'./dumps/TikTokVideo_dump_{timestamp}.csv'
        chunk_size = options.get('chunk_size')
        export_tiktok_videos_to_csv(videos, output_path, chunk_size)
