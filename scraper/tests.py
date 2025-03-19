from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import override_settings, TestCase
from django.urls import reverse
from django.utils.timezone import make_aware, now
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from ddm.projects.models import ResearchProfile

from scraper.models import TikTokVideo, Hashtag, TikTokUser, TikTokVideo_B, TikTokUser_B


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
        for i in range(1048):
            video = TikTokVideo.objects.create(
                video_id=1000 + i,
                video_description=f'Video {i}',
                create_time=make_aware(datetime(2024, 2, 1, 12, 0, 0)),
                author_id=self.tt_user1,
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
            author_id=self.tt_user1,
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
            author_id=self.tt_user2,
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
        self.assertEqual(len(response.data['results']), 1000)

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
            'author_id',
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


class TikTokVideoBDetailViewTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.tt_user = TikTokUser_B.objects.create(author_id='123', username='test')

        # Video with `scrape_date=None` (Should allow updates)
        self.video1 = TikTokVideo_B.objects.create(
            video_id='123456',
            video_description='Initial description',
            like_count=1000,
            scrape_date=None,  # Allows updates
            author_id=self.tt_user
        )

        # Video with `scrape_date` set (Should block updates)
        self.video2 = TikTokVideo_B.objects.create(
            video_id='789101',
            video_description='Locked video',
            like_count=5000,
            scrape_date='2023-01-01T00:00:00Z',
            author_id=self.tt_user
        )

        self.hashtag1 = Hashtag.objects.create(name='funny')
        self.hashtag2 = Hashtag.objects.create(name='funnier')
        self.video1.hashtags.add(self.hashtag1)
        self.video1.hashtags.add(self.hashtag2)

        # Add user to create auth token.
        self.credentials = {'username': 'user', 'password': '<PASSWORD>'}
        self.user = User.objects.create_user(
            **self.credentials, **{'email': 'owner@mail.com'})
        ResearchProfile.objects.create(user=self.user)
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_video(self):
        """Test retrieving a video by video_id."""
        url = reverse('video_b_detail_api', kwargs={'video_id': self.video1.video_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['video_id'], '123456')
        self.assertEqual(response.data['video_description'], 'Initial description')
        self.assertEqual(response.data['author_id'], '123')
        self.assertEqual(response.data['author_username'], 'test')
        self.assertEqual(response.data['hashtags'], ['funny', 'funnier'])

    def test_update_video_allowed(self):
        """Test updating a video when scrape_date=None."""
        url = reverse('video_b_detail_api', kwargs={'video_id': self.video1.video_id})
        response = self.client.post(
            url,
            {'video_description': 'Updated description'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.video1.refresh_from_db()
        self.assertEqual(self.video1.video_description, 'Updated description')

    def test_update_video_blocked(self):
        """Test updating a video when scrape_date is set."""
        url = reverse('video_b_detail_api', kwargs={'video_id': self.video2.video_id})
        response = self.client.post(
            url,
            {'video_description': 'Should not update'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.video2.refresh_from_db()
        self.assertEqual(self.video2.video_description, 'Locked video')  # Should remain unchanged

    def test_put_video_not_allowed(self):
        """Test that full updates (PUT) are blocked."""
        url = reverse('video_b_detail_api', kwargs={'video_id': self.video1.video_id})
        response = self.client.put(
            url,
            {'video_description': 'Full update attempt', 'like_count': 2000},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  # If PUT is blocked


class TikTokVideoBRetrieveUpdateAPIPostTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.existing_user = TikTokUser_B.objects.create(username="existing_user")

        self.hashtag1 = Hashtag.objects.create(name="funny")
        self.hashtag2 = Hashtag.objects.create(name="dance")

        self.video1 = TikTokVideo_B.objects.create(
            video_id="123456",
            video_description="Original description",
            like_count=100,
            author_id=self.existing_user,
            scrape_date=None
        )
        self.video1.hashtags.set([self.hashtag1])

        self.video2 = TikTokVideo_B.objects.create(
            video_id="789101",
            video_description="Locked video",
            like_count=5000,
            scrape_date=now()
        )

        # Add user to create auth token.
        self.credentials = {'username': 'user', 'password': '<PASSWORD>'}
        self.user = User.objects.create_user(
            **self.credentials, **{'email': 'owner@mail.com'})
        ResearchProfile.objects.create(user=self.user)
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_update_video_when_scrape_date_is_none(self):
        """POST should update a video when `scrape_date = None`."""
        data = {
            'video_description': 'these arms are for cake throwing 🎂 #guilty #foryou #liveshow ',
            'create_time': '2024-08-22T00:22:01+02:00',
            'author_id': '89645703060140032',
            'comment_count': 1998,
            'like_count': 1000000,
            'share_count': 23300,
            'view_count': 6200000,
            'music_id': 7402649657337318175,
            'region_code': 'US',
            'schedule_time': 0,
            'is_ad': False,
            'suggested_words': '[]',
            'diggcount': 1000000,
            'collectcount': 33249,
            'repostcount': 0,
            'poi_name': None,
            'poi_address': None,
            'poi_city': None,
            'warn_info': [],
            'original_item': False,
            'offical_item': False,
            'secret': False,
            'for_friend': False,
            'digged': False,
            'item_comment_status': 0,
            'take_down': 0,
            'effect_stickers': None,
            'private_item': False,
            'duet_enabled': True,
            'stitch_enabled': True,
            'stickers_on_item': [{'stickerText': ['When i’m being chased by the police and overhear them say “the suspect has luscious long hair and great throwing arms”'], 'stickerType': 4}],
            'share_enabled': True,
            'comments': None,
            'duet_display': 0,
            'stitch_display': None,
            'index_enabled': True,
            'diversification_labels': ['Comedy', 'Performance'],
            'diversification_id': 10003,
            'channel_tags': [],
            'keyword_tags': [{'pageType': 0, 'keyword': 'devon-aoki-sekarang'}, {'pageType': 0, 'keyword': 'devon-aoki-speaking-french'}, {'pageType': 0, 'keyword': 'devon-aoki-hijos'}, {'pageType': 0, 'keyword': 'devon-aoki-car'}, {'pageType': 0, 'keyword': 'steve-aoki-married-2024'}, {'pageType': 0, 'keyword': 'devon-aoki-today'}, {'pageType': 0, 'keyword': 'devon-aoki-lenny-kravitz'}, {'pageType': 0, 'keyword': 'devon-aoki-2025'}, {'pageType': 0, 'keyword': 'devon-aoki-downsyndrome'}, {'pageType': 0, 'keyword': 'devon-aoki-tiktok'}],
            'is_ai_gc': False,
            'ai_gc_description': None,
            'filepath': 'data/tiktok_7405721540819537194_*',
            'duration': 14,
            'height': 1024,
            'width': 576,
            'ratio': 540,
            'volume_loudness': -24.9,
            'volume_peak': 0.26915,
            'has_original_audio': False,
            'enable_audio_caption': True,
            'no_caption_reason': 3,
            'content_downloaded': False,
            'scrape_priority': 0,
            'scrape_success': False,
            'scrape_status': None,
            'scrape_date': '2025-03-10T10:10:18.883833+01:00',
            'hashtags': ['foryou', 'liveshow', 'guilty'], 'mentions': []
        }

        url = reverse("video_b_detail_api",
                      kwargs={"video_id": self.video1.video_id})
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        old_user_pk = self.video1.author_id.pk
        self.video1.refresh_from_db()

        # Check that the fields are updated
        self.assertEqual(self.video1.video_description, 'these arms are for cake throwing 🎂 #guilty #foryou #liveshow')
        self.assertEqual(self.video1.like_count, 1000000)

        # Check that the author has changed
        self.assertEqual(self.video1.author_id.username, "<<placeholder until scraped>>")
        self.assertNotEqual(self.video1.author_id.pk, old_user_pk)

        # Check that new hashtags were created and assigned
        hashtags = list(self.video1.hashtags.values_list("name", flat=True))
        self.assertCountEqual(hashtags, ['foryou', 'liveshow', 'guilty'])

    def test_update_fails_when_scrape_date_is_set(self):
        """POST should be blocked if `scrape_date` is not None."""
        data = {
            "video_description": "Should not update"
        }

        url = reverse("video_b_detail_api",
                      kwargs={"video_id": self.video2.video_id})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.video2.refresh_from_db()
        self.assertEqual(self.video2.video_description, "Locked video")

    def test_update_creates_new_author_if_not_exists(self):
        """POST should create a new TikTokUser_B if author_id does not exist."""
        data = {
            "author_id": "123"
        }

        url = reverse("video_b_detail_api",
                      kwargs={"video_id": self.video1.video_id})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        old_user_pk = self.video1.author_id.pk
        self.video1.refresh_from_db()
        self.assertEqual(self.video1.author_id.username, "<<placeholder until scraped>>")
        self.assertNotEqual(self.video1.author_id.pk, old_user_pk)

        # Verify that a new user was actually created
        self.assertTrue(TikTokUser_B.objects.filter(author_id="123").exists())

    def test_update_creates_new_hashtags_if_not_exists(self):
        """POST should create new hashtags if they do not exist and assign them to the video."""
        data = {
            "hashtags": ["newtag1", "newtag2"]
        }

        url = reverse("video_b_detail_api",
                      kwargs={"video_id": self.video1.video_id})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.video1.refresh_from_db()

        # Verify that new hashtags were created
        self.assertTrue(Hashtag.objects.filter(name="newtag1").exists())
        self.assertTrue(Hashtag.objects.filter(name="newtag2").exists())

        # Verify that the video has been updated with the new hashtags
        hashtags = list(self.video1.hashtags.values_list("name", flat=True))
        self.assertCountEqual(hashtags, ["newtag1", "newtag2"])

    def test_update_replaces_existing_hashtags(self):
        """POST should replace existing hashtags with the new ones provided."""
        data = {
            "hashtags": ["replacedTag"]
        }

        url = reverse("video_b_detail_api",
                      kwargs={"video_id": self.video1.video_id})
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.video1.refresh_from_db()

        # Verify that old hashtags are replaced
        hashtags = list(self.video1.hashtags.values_list("name", flat=True))
        self.assertCountEqual(hashtags, ["replacedTag"])


class TikTokVideoBListAPITest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.tt_user = TikTokUser_B.objects.create(id=1, username='test_user')

        # Create hashtags.
        self.hashtag1 = Hashtag.objects.create(name='funny')
        self.hashtag2 = Hashtag.objects.create(name='dance')

        # Create videos.
        self.video1 = TikTokVideo_B.objects.create(
            video_id='123456',
            video_description='Funny video',
            create_time=make_aware(datetime(2024, 3, 10)),
            scrape_date=None,
            content_downloaded=True,
            is_ad=False,
            author_id=self.tt_user
        )
        self.video1.hashtags.add(self.hashtag1)

        self.video2 = TikTokVideo_B.objects.create(
            video_id='789101',
            video_description='Dance video',
            create_time=make_aware(datetime(2024, 3, 5)),
            scrape_date=make_aware(datetime(2024, 3, 6)),
            content_downloaded=False,
            is_ad=True,
            author_id=self.tt_user
        )
        self.video2.hashtags.add(self.hashtag2)

        # Add user to create auth token.
        self.credentials = {'username': 'user', 'password': '<PASSWORD>'}
        self.user = User.objects.create_user(
            **self.credentials, **{'email': 'owner@mail.com'})
        ResearchProfile.objects.create(user=self.user)
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.api_url = reverse('video_b_list_api')

    def test_get_video_list(self):
        """Test retrieving the list of videos."""
        response = self.client.get(self.api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_scrape_date(self):
        """Test filtering videos by scrape_date."""
        response = self.client.get(self.api_url + '?scrape_date=2024-03-06')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['video_id'], '789101')

    def test_filter_by_content_downloaded(self):
        """Test filtering videos by content_downloaded=True."""
        response = self.client.get(self.api_url + '?content_downloaded=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['video_id'], '123456')

    def test_filter_by_is_ad(self):
        """Test filtering videos by is_ad=True."""
        response = self.client.get(self.api_url + '?is_ad=True')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['video_id'], '789101')

    def test_filter_by_author_id(self):
        """Test filtering videos by author_id."""
        response = self.client.get(self.api_url + f'?author_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_by_hashtags(self):
        """Test filtering videos by hashtags (funny)."""
        response = self.client.get(self.api_url + '?hashtags=funny')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['video_id'], '123456')

    def test_filter_by_multiple_hashtags(self):
        """Test filtering videos by multiple hashtags (funny, dance)."""
        response = self.client.get(self.api_url + '?hashtags=funny,dance')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
