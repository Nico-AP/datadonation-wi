import logging
from datetime import datetime

from django.db import transaction
from django.http import Http404
from django.utils.timezone import make_aware
from http import HTTPStatus

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from scraper.models import TikTokVideo, TikTokVideo_B, TikTokUser_B, Hashtag
from scraper.scraper import save_video_to_db
from scraper.serializers import TikTokVideoSerializer, TikTokVideoBSerializer

logger = logging.getLogger('api_logger')


class ScraperPostAPI(APIView):
    """
    View to remotely add new entries for TikTok videos to the database.

    Expects raw JSON data in the payload.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_scrapets(self):
        """
        Returns the participant object. If no Participant object is found,
        returns a http 404 response.
        """
        return self.request.query_params.get('scrapets')

    def post(self, request, *args, **kwargs):
        post_data = request.data
        post_errors = 0
        n_posted = 0
        scrape_ts = self.get_scrapets()
        if scrape_ts is not None:
            try:
                print(scrape_ts)
                scrape_ts = float(scrape_ts)
            except ValueError:
                msg = (
                    'Invalid format of url parameter scrapets provided. '
                    'Must be convertible to float.'
                )
                return Response(
                    {'message': msg},
                    status=HTTPStatus.UNPROCESSABLE_ENTITY
                )

        for entry in post_data:
            try:
                save_video_to_db(entry, scrape_ts)
                n_posted += 1
            except Exception as e:
                logger.info(
                    f'Video: {entry.get("id")}; Exception: {e}'
                )
                post_errors += 1

        msg = (
            f'Imported {n_posted} records successfully. '
            f'{post_errors} were skipped due to an error.'
        )
        return Response({'message': msg}, status=status.HTTP_201_CREATED)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class TikTokVideoListAPI(ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = TikTokVideo.objects.all().order_by('-create_time')
    serializer_class = TikTokVideoSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """
        Optionally filters the returned videos for a specific create_date or
        a specific TikTok user.

        Optional query parameters:
        - date (in the format %Y-%m-%d)
        - username
        """
        queryset = self.queryset

        create_date = self.request.query_params.get('date')
        if create_date is not None:
            date = make_aware(datetime.strptime(create_date, '%Y-%m-%d'))
            queryset = queryset.filter(create_time__date=date)

        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(author_id__name=username)

        return queryset


class TikTokVideoBRetrieveAPI(APIView):
    """
    Endpoint to get (GET) or update (POST) single TikTokVideo_B instance.

    Examples:
        GET apis/video/<video_id>/

        POST apis/video/<video_id>/
        Content-Type: application/json
        {
            "video_description": "Updated description",
            "like_count": 5000
        }

    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TikTokVideoBSerializer

    def get(self, request, *args, **kwargs):
        """Retrieve a TikTokVideo_B instance."""
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def get_object(self):
        """Retrieve a video object using `video_id` from the URL kwargs."""
        video_id = self.kwargs.get('video_id')
        if not video_id:
            raise Http404('Missing video_id in URL')
        try:
            return TikTokVideo_B.objects.get(video_id=video_id)
        except TikTokVideo_B.DoesNotExist:
            raise Http404('Video not found')


class TikTokVideoBUpdateAPI(APIView):
    """
    Endpoint to update (POST) single TikTokVideo_B instance.

    Examples:
        POST apis/video/<video_id>/update/
        Content-Type: application/json
        {
            "video_description": "Updated description",
            "like_count": 5000
        }

    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TikTokVideoBSerializer

    def get_object(self):
        """Retrieve a video object using `video_id` from the URL kwargs."""
        video_id = self.kwargs.get('video_id')
        if not video_id:
            raise Http404('Missing video_id in URL')
        try:
            return TikTokVideo_B.objects.get(video_id=video_id)
        except TikTokVideo_B.DoesNotExist:
            raise Http404('Video not found')

    def post(self, request, *args, **kwargs):
        """
        Only allow updating videos where scrape_date = None, i.e., videos
        that have not been scraped yet. The assumption is that the earlier
        scrape attempts are more likely to have been successful.
        """
        # Only allow POST of data belonging to existing objects.
        instance = self.get_object()

        # Only allow updates of videos where scrape_date = None
        if instance.scrape_date is not None:
            return Response(
                {'error': 'The metadata for this video have already been scraped. Updates are only allowed for videos with scrape_date = None.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract data from request.
        data = request.data.copy()

        # Get or create TikTokUser_B
        with transaction.atomic():
            author_id = data.pop('author_id', None)
            if author_id:
                author, created = TikTokUser_B.objects.get_or_create(author_id=author_id)
                if created:
                    author.username = '<<placeholder until scraped>>'
                    author.save()
                instance.author_id = author  # Update author_id field

            # Get or create hashtag objects
            hashtags_list = data.pop('hashtags', [])
            if hashtags_list:
                hashtags = []
                for tag_name in hashtags_list:
                    hashtag, _ = Hashtag.objects.get_or_create(name=tag_name)
                    hashtags.append(hashtag)

                # Set the hashtags for the video
                instance.hashtags.set(hashtags)

            mentions_list = data.pop('mentions', [])
            if mentions_list:
                mentions = [TikTokUser_B.objects.get_or_create(author_id=user_id)[0] for user_id in mentions_list]
                instance.mentions.set(mentions)

            instance.save()

            serializer = self.serializer_class(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(serializer.data)


class TikTokBResultsSetPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 2000


class TikTokVideoBFilter(filters.FilterSet):
    hashtags = filters.CharFilter(method='filter_hashtags')

    def filter_hashtags(self, queryset, name, value):
        """Filters videos by hashtags (comma-separated)."""
        hashtag_list = value.split(',')
        return queryset.filter(hashtags__name__in=hashtag_list).distinct()

    class Meta:
        model = TikTokVideo_B
        exclude = [
            'warn_info',
            'effect_stickers',
            'stickers_on_item',
            'comments',
            'diversification_labels',
            'channel_tags',
            'keyword_tags'
        ]


class TikTokVideoBListAPI(ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = TikTokVideo_B.objects.all().order_by('-create_time')
    serializer_class = TikTokVideoBSerializer
    pagination_class = TikTokBResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TikTokVideoBFilter
