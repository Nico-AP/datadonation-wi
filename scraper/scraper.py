import json
import logging
import os
import pandas as pd
import re
import requests
import time
from datetime import datetime, date, timedelta

from django.utils import timezone
from django.utils.timezone import make_aware
from dotenv import load_dotenv
from scraper.hashtags import HASHTAG_LIST
from scraper.models import TikTokVideo, Hashtag, TikTokUser

load_dotenv()

logger = logging.getLogger('scraper_logger')


def generate_date_range(start_date, end_date):
    """
    Generate a list of date sections for scraping periods beyond the 30-day API limit.

    Args:
        start_date (str): Start date in YYYYMMDD format
        end_date (str): End date in YYYYMMDD format

    Returns:
        list: List of tuples containing (start_date, end_date) pairs in YYYYMMDD format

    Example:
        >>> generate_date_range('20230101', '20230215')
        [('20230101', '20230130'), ('20230131', '20230215')]
    """
    # Convert YYYYMMDD to datetime objects
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")

    dates = []
    current_date = start

    while current_date <= end:
        days_remaining = (end - current_date).days

        if days_remaining <= 30:
            dates.append((
                current_date.strftime("%Y%m%d"),
                end.strftime("%Y%m%d")
            ))
            break
        else:
            period_end = current_date + timedelta(days=29)
            dates.append((
                current_date.strftime("%Y%m%d"),
                period_end.strftime("%Y%m%d")
            ))
            current_date = period_end + timedelta(days=1)

    return dates


def get_username_list():
    df = pd.read_csv('./reports/static/reports/csv/actor_party_mapping.csv')
    pattern = r"@(.*)"
    usernames = [re.findall(pattern, i)[0] for i in df['SM_TikTokURL']]
    return usernames


def get_formatted_date(delay=4):
    """
    Get current date minus 4 days in the format %Y%m%d (e.g., '20241224').
    """
    current_date = date.today() - timedelta(days=delay)
    formatted_date = current_date.strftime('%Y%m%d')
    return formatted_date


def request_access_token():
    """ Function to make first call to API to get the access token. """
    client_key = os.environ.get('TT_API_CLIENT_KEY')
    client_secret = os.environ.get('TT_API_CLIENT_SECRET')

    # Set request parameters.
    base_url = 'https://open.tiktokapis.com/v2/oauth/token/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    payload = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    # Request bearer auth token.
    response = requests.post(base_url, headers=headers, data=payload)
    response_as_json = response.json()
    access_token = response_as_json['access_token']
    return access_token


def log_server_ip():
    """Added to test IP-related issues."""
    response = requests.get('https://api.ipify.org?format=json')
    logger.info(f'Server IP: {response.json()["ip"]}')
    return


def get_video_query_url():
    base_url = 'https://open.tiktokapis.com/v2/research/video/query/'
    query_fields = [
        'id',
        'video_description',
        'create_time',
        'region_code',
        'share_count',
        'view_count',
        'like_count',
        'comment_count',
        'music_id',
        'hashtag_names',
        'username',
        'voice_to_text'
    ]
    query_url = base_url + '?fields=' + ','.join(query_fields)
    return query_url


def scrape_videos_pagination(url, usernames, hashtags, max_count,
                             start_date, end_date, headers, search_id, cursor):
    """Get video data from TikTok API."""
    query_params = {
        'query': {
            'or': [
                {
                    'operation': 'IN',
                    'field_name': 'username',
                    'field_values': usernames
                },
                {
                    'operation': 'IN',
                    'field_name': 'hashtag_name',
                    'field_values': hashtags
                }
            ],
            'and': [
                {
                    'operation': 'IN', 'field_name': 'region_code',
                    'field_values': [
                        'DE', 'de', 'RU', 'ru', 'AT', 'at', 'ch', 'CH'
                    ]
                }
            ]
        },
        'max_count': max_count,
        'is_random': False,
        'start_date': start_date,
        'end_date': end_date,
        'cursor': cursor
    }

    # Only add search_id if it exists
    if search_id:
        query_params['search_id'] = search_id

    # Make the call and transform the response to a JSON file.
    response = requests.post(
        url, headers=headers, data=json.dumps(query_params))
    # Return the response parsed as a JSON file.
    return response



def scrape_videos_accounts_only(url, usernames, max_count,
                                start_date, end_date, headers,
                                search_id, cursor):
    """
    Get video data from TikTok API for accounts only.
    """
    query_params = {
        'query': {
            'or': [
                {
                    'operation': 'IN',
                    'field_name': 'username',
                    'field_values': usernames
                }
            ],
            'and': [
                {
                    'operation': 'IN', 'field_name': 'region_code',
                    'field_values': [
                        'DE', 'de', 'RU', 'ru', 'AT', 'at', 'ch', 'CH'
                    ]
                }
            ]
        },
        'max_count': max_count,
        'is_random': False,
        'start_date': start_date,
        'end_date': end_date,
        'cursor': cursor,
        'search_id': search_id
    }
    # Make the call and transform the response to a JSON file.
    response = requests.post(
        url, headers=headers, data=json.dumps(query_params))
    # Return the response parsed as a JSON file.
    return response


def get_datetime_from_unix_ts(unix_ts):
    return datetime.fromtimestamp(unix_ts, timezone.utc)


def save_videos_to_file(videos, start_date, search_id, cursor):
    """ Save retrieved data to JSON file. """
    file_name = f'{start_date}_{search_id}_{cursor - 100}.json'
    save_directory = 'scraper/data'
    file_path = os.path.join(save_directory, file_name)
    json_string = json.dumps(videos)
    with open(file_path, 'w') as f:
        json.dump(json_string, f)
    return


def get_datetime_from_ts(ts):
    naive_datetime = datetime.fromtimestamp(ts)
    return make_aware(naive_datetime)


def save_video_to_db(video_data, scrape_ts=None):
    """
    Saves video data to database.

    Creates new video if no video exists in the db with the ID included in
    video_data.
    If a video already exists, the existing video is updated if scrape_ts is
    newser than video.scrape_date.

    scrape_ts must be provided in Unix timestamp format
    """
    try:
        # Debug log the video data
        logger.info(f"Saving video data: {video_data.get('id')}")
        logger.debug(f"Video data: {video_data}")

        tt_user, _ = TikTokUser.objects.get_or_create(name=video_data.get('username'))

        video = TikTokVideo.objects.filter(video_id=video_data.get('id')).first()
        if video is None:
            video = TikTokVideo.objects.create(
                video_id=video_data.get('id'),
                video_description=video_data.get('video_description'),
                create_time=get_datetime_from_unix_ts(video_data.get('create_time')),
                username=tt_user,

                comment_count=video_data.get('comment_count'),
                like_count=video_data.get('like_count'),
                share_count=video_data.get('share_count'),
                view_count=video_data.get('view_count'),

                music_id=video_data.get('music_id'),
                region_code=video_data.get('region_code'),
            )

            if scrape_ts:
                video.scrape_date = get_datetime_from_ts(scrape_ts)
                video.save()

            video_hashtags = []
            for hashtag in video_data['hashtag_names']:
                video_hashtags.append(Hashtag.objects.get_or_create(name=hashtag)[0])
            video.hashtags.set(video_hashtags)

        else:
            scrape_date = get_datetime_from_ts(scrape_ts)
            if scrape_date > video.scrape_date:
                video.comment_count = video_data.get('comment_count')
                video.like_count = video_data.get('like_count')
                video.share_count = video_data.get('share_count')
                video.view_count = video_data.get('view_count')
                video.scrape_date = scrape_date
                video.save()
        return

    except Exception as e:
        logger.error(f"Error saving video {video.get('id', 'unknown')}: {str(e)}")
        logger.error(f"Video data: {video}")
        raise


def save_videos_to_db(videos, scrape_ts=None):
    for video in videos:
        try:
            save_video_to_db(video, scrape_ts)
        except Exception as e:
            logger.error(
                f'Video: {video.get("id")}; Exception: {e}'
            )
    return


def get_tt_videos_new_day(specific_date=None):
    logger.info('========Scraping I new day videos========')
    access_token = request_access_token()

    # Set query parameter.
    if specific_date:
        start_date = specific_date
        end_date = specific_date
    else:
        start_date = get_formatted_date()
        end_date = get_formatted_date()

    usernames = get_username_list()
    hashtags = HASHTAG_LIST

    url = get_video_query_url()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    max_count = 100
    cursor = 0

    # Set utility parameter.
    search_id = ''
    has_more = True
    error_counter = 0

    scrape_date = timezone.now().timestamp()

    while has_more is True:
        try:
            response = scrape_videos_pagination(
                url, usernames, hashtags, max_count,
                start_date, end_date, headers, search_id, cursor
            )
            logger.info(f'Response status code: {response.status_code}')
            temp_data = response.json()

            # Log full response for debugging
            logger.debug(f"Full API response: {temp_data}")

            if 'error' in temp_data and temp_data['error'].get('code') in ['internal_error', 'invalid_params']:
                error_counter += 1
                logger.warning(f'Error encountered: {temp_data["error"]["message"]} ({error_counter})')
                logger.warning(f'Error code: {temp_data["error"]["code"]}')

                if error_counter >= 20:
                    has_more = False
                    logger.error(
                        f'Stopping after {error_counter} consecutive errors. '
                        f'Last error: {temp_data["error"]["message"]}'
                    )
                else:
                    time.sleep(10)
                continue

            # Reset error counter on successful request
            error_counter = 0

            # Check if we have data
            if 'data' not in temp_data:
                logger.error(f"Unexpected API response format: {temp_data}")
                break

            data = temp_data['data']
            logger.info(
                f'Request successful. Cursor: {data.get("cursor", 0)}, '
                f'Has More: {data.get("has_more", False)}'
            )

            # Update query parameters
            cursor = data.get('cursor', 0)
            has_more = data.get('has_more', False)
            search_id = data.get('search_id', '')

            if 'videos' in data:
                save_videos_to_db(data['videos'], scrape_date)

            time.sleep(10)

        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            logger.error("Full traceback:", exc_info=True)
            raise


def get_tt_videos_update_account_data():
    logger.info('========Scraping II update account data========')
    access_token = request_access_token()

    # Set query parameter.
    start_date = "20250101"  # Changed back to YYYYMMDD format
    end_date = get_formatted_date(delay=5)  # Already returns YYYYMMDD

    logger.info(f"Generating date range from {start_date} to {end_date}")
    date_ranges = generate_date_range(start_date, end_date)
    logger.info(f"Generated {len(date_ranges)} date ranges")

    usernames = get_username_list()

    url = get_video_query_url()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    max_count = 100

    scrape_date = timezone.now().timestamp()

    for date_range in date_ranges:
        print(date_range)
        start_date = date_range[0]
        end_date = date_range[1]
        # Set utility parameter.
        search_id = ''
        has_more = True
        error_counter = 0
        cursor = 0

        while has_more is True:
            response = scrape_videos_accounts_only(
                url, usernames, max_count,
                start_date, end_date, headers, search_id, cursor
            )
            logger.info(f'Response status code: {response.status_code}')
            print(response.status_code)
            temp_data = response.json()

            if (temp_data['error']['code'] == 'internal_error') | \
                    (temp_data['error']['code'] == 'invalid_params'):
                error_counter += 1
                logger.warning(f'Error encountered: {temp_data["error"]["message"]} ({error_counter})')
                logger.warning(f'Error code: {temp_data["error"]["code"]}')

                # Killswitch after 20 consecutive errors.
                if error_counter >= 20:
                    has_more = False
                    logger.error(
                        f'Stopping after {error_counter} consecutive errors. '
                        f'Last error: {temp_data["error"]["message"]}'
                    )
                else:
                    time.sleep(10)
            else:
                error_counter = 0
                logger.info(
                    f'Request successful. Cursor: {temp_data["data"]["cursor"]}, '
                    f'Has More: {temp_data["data"]["has_more"]}'
                )

                # Update query parameter based on previous request.
                cursor = temp_data['data']['cursor']
                has_more = temp_data['data']['has_more']
                search_id = temp_data['data']['search_id']

                retrieved_data = temp_data['data']['videos']
                # save_videos_to_file(
                #   retrieved_data, start_date, search_id, cursor)
                save_videos_to_db(retrieved_data, scrape_date)

                time.sleep(10)

                if not has_more:
                    logger.info(
                        f'Report for scraping {get_formatted_date()}. '
                        f'Successfully scraped {cursor} videos'
                    )

    # Add this to test IP-related issues.
    log_server_ip()
