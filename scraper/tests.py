from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from ddm.projects.models import ResearchProfile

from scraper.models import TikTokVideo, Hashtag, TikTokUser

User = get_user_model()


class ScraperPostAPITestCase(APITestCase):
    """ Tests for the ScraperPostAPI. """

    @override_settings(SECURE_SSL_REDIRECT=False)
    def setUp(self):
        """ Setup test user and authentication token. """
        self.client.defaults['HTTP_X_FORWARDED_PROTO'] = 'https'
        self.client.defaults['wsgi.url_scheme'] = 'https'

        self.credentials = {'username': 'user', 'password': '<PASSWORD>'}
        self.user = User.objects.create_user(
            **self.credentials, **{'email': 'owner@mail.com'})
        ResearchProfile.objects.create(user=self.user)

        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('scraper_post_api')

        self.valid_video_data = [
            {
                "comment_count": 25,
                "hashtag_names": ["hashtag1", "hashtag2"],
                "like_count": 146,
                "music_id": 7068650753636501506,
                "share_count": 0,
                "username": "someuser",
                "video_description": "Some Description",
                "create_time": 1733510690,
                "id": 7445371706207669526,
                "region_code": "DE",
                "view_count": 1318
            },
            {
                "comment_count": 25,
                "hashtag_names": ["hashtag1", "hashtag3"],
                "like_count": 146,
                "music_id": 7068650753456501506,
                "share_count": 8,
                "username": "some-other-user",
                "video_description": "Some Description",
                "create_time": 1733510690,
                "id": 7445371712307669526,
                "region_code": "DE",
                "view_count": 1318
            },
        ]

        self.invalid_video_data = [
            {
                "comment_count": 25,
                "hashtag_names": ["hashtag1", "hashtag2"],
                "like_count": 146,
                "music_id": 7068650753636501506,
                "share_count": 0,
                "username": "someuser",
                "video_description": "Some Description",
                "create_time": 1733510690,
                "id": 7445371706207669526,
                "region_code": "DE",
                "view_count": 1318
            },
            {
                "comment_count": 25,
                "region_code": "DE",
                "view_count": 1318
            },
        ]

    def test_authenticated_post_success(self):
        """
        Test that an authenticated user can post valid video data successfully.
        """
        response = self.client.post(self.url, self.valid_video_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Imported 2 records successfully', response.data['message'])

    def test_authenticated_post_with_invalid_entries(self):
        """ Test that the API correctly logs errors when given invalid data. """
        response = self.client.post(self.url, self.invalid_video_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Imported 1 records successfully', response.data['message'])
        self.assertIn('1 were skipped due to an error.', response.data['message'])

    def test_unauthenticated_post_fails(self):
        """ Test that unauthenticated users cannot post data. """
        self.client.credentials()  # Remove authentication
        response = self.client.post(self.url, self.valid_video_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_post_request(self):
        """
        Test that sending an empty request returns a success message with 0 records.
        """
        response = self.client.post(self.url, [], format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Imported 0 records successfully', response.data['message'])


class TikTokVideoListAPITestCase(APITestCase):
    """ Tests for the TikTokVideoListAPIView. """

    @override_settings(SECURE_SSL_REDIRECT=False)
    def setUp(self):
        """Setup test data for the API."""
        self.client.defaults['HTTP_X_FORWARDED_PROTO'] = 'https'
        self.client.defaults['wsgi.url_scheme'] = 'https'

        self.credentials = {'username': 'user', 'password': '<PASSWORD>'}
        self.user = User.objects.create_user(
            **self.credentials, **{'email': 'owner@mail.com'})
        ResearchProfile.objects.create(user=self.user)

        self.tt_user1 = TikTokUser.objects.create(name='some name')
        self.tt_user2 = TikTokUser.objects.create(name='another name')
        self.hashtag1 = Hashtag.objects.create(name='funny')
        self.hashtag2 = Hashtag.objects.create(name='dance')

        # Create multiple TikTokVideo instances for pagination testing.
        for i in range(148):
            video = TikTokVideo.objects.create(
                video_id=1000 + i,
                video_description=f'Video {i}',
                create_time=make_aware(datetime(2024, 2, 1, 12, 0, 0)),
                username=self.tt_user1,
                comment_count=10 * i,
                like_count=100 * i,
                share_count=5 * i,
                view_count=1000 * i,
                music_id=2000 + i,
                region_code='US',
            )
            video.hashtags.add(self.hashtag1, self.hashtag2)  # Associate hashtags

        video = TikTokVideo.objects.create(
            video_id=101,
            video_description=f'Video 101',
            create_time=make_aware(datetime(2024, 4, 1, 12, 0, 0)),
            username=self.tt_user1,
            comment_count=10 * i,
            like_count=100 * i,
            share_count=5 * i,
            view_count=1000 * i,
            music_id=2000 + i,
            region_code='US',
        )
        video.hashtags.add(self.hashtag1, self.hashtag2)

        video = TikTokVideo.objects.create(
            video_id=102,
            video_description=f'Video 102',
            create_time=make_aware(datetime(2024, 4, 1, 12, 0, 0)),
            username=self.tt_user2,
            comment_count=10 * i,
            like_count=100 * i,
            share_count=5 * i,
            view_count=1000 * i,
            music_id=2000 + i,
            region_code='US',
        )
        video.hashtags.add(self.hashtag1, self.hashtag2)

        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('video_list_api')

    def test_video_list_success(self):
        """ Test that the API returns a paginated list of videos. """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 100)

        # Ensure pagination is present
        self.assertIn('next', response.data)
        self.assertIsNotNone(response.data['next'])  # Next page should exist
        self.assertIn('previous', response.data)
        self.assertIsNone(response.data['previous'])  # No previous on first page

    def test_video_list_unauthenticated_fails(self):
        """ Test that unauthenticated users cannot get data. """
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination_next_page(self):
        """ Test that pagination correctly moves to the next page. """
        response_page_1 = self.client.get(self.url)
        next_page_url = response_page_1.data['next']

        response_page_2 = self.client.get(next_page_url)

        self.assertEqual(response_page_2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_page_2.data['results']), 50)
        self.assertIn('previous', response_page_2.data)
        self.assertIsNotNone(response_page_2.data['previous'])

    def test_empty_database(self):
        """ Test that the API handles an empty database gracefully. """
        TikTokVideo.objects.all().delete()  # Remove all videos
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_video_fields_in_response(self):
        """ Test that the API returns the expected fields in the response. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_video = response.data['results'][0]

        expected_fields = {
            'video_id',
            'video_description',
            'create_time',
            'username',
            'comment_count',
            'like_count',
            'share_count',
            'view_count',
            'hashtags',
            'music_id',
            'region_code',
        }
        self.assertTrue(expected_fields.issubset(first_video.keys()))

    def test_filter_by_date(self):
        """
        Test that filtering by 'date' returns only videos from that specific date.
        """
        response = self.client.get(f'{self.url}?date=2024-04-01')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_username(self):
        """
        Test that filtering by 'username' returns only videos for that specific user.
        """
        response = self.client.get(f'{self.url}?username=another name')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['video_id'], 102)
