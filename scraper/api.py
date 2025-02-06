import logging
from datetime import datetime

from django.utils.timezone import make_aware
from http import HTTPStatus
from rest_framework import authentication, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from scraper.models import TikTokVideo
from scraper.scraper import save_video_to_db
from scraper.serializers import TikTokVideoSerializer

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


class TikTokVideoListAPI(ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = TikTokVideo.objects.all().order_by('-create_time')
    serializer_class = TikTokVideoSerializer

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
            queryset = queryset.filter(username__name=username)

        return queryset
