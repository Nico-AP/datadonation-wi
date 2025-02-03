import datetime
import json
import logging
import os
import pandas as pd
import re
import requests
import time

from django.utils import timezone
from dotenv import load_dotenv
from scraper.hashtags import HASHTAG_LIST
from scraper.models import TikTokVideo, Hashtag, TikTokUser

load_dotenv()


def configure_logging():
    logging.basicConfig(
        filename='scraper/scraper.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return


def get_username_list():
    df = pd.read_csv('scraper/df_actors_fused_list.csv')
    pattern = r"@(.*)"
    usernames = [re.findall(pattern, i)[0] for i in df['SM_TikTokURL']]
    return usernames


def get_formatted_date():
    """
    Get current date minus 4 days in the format %Y%m%d (e.g., '20241224').
    """
    current_date = datetime.date.today() - datetime.timedelta(days=4)
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
    logging.info(f'Server IP: {response.json()["ip"]}')
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
                {'operation': 'IN', 'field_name': 'username', 'field_values': usernames},
                {'operation': 'IN', 'field_name': 'hashtag_name', 'field_values': hashtags}
            ],
            'and': [
                {'operation': 'IN', 'field_name': 'region_code',
                 'field_values': ['DE', 'de', 'RU', 'ru', 'AT', 'at', 'ch', 'CH']}
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
    response = requests.post(url, headers=headers, data=json.dumps(query_params))
    # Return the response parsed as a JSON file.
    return response


def get_datetime_from_unix_ts(unix_ts):
    return datetime.datetime.fromtimestamp(unix_ts, timezone.utc)


def save_videos_to_file(videos, start_date, search_id, cursor):
    """ Save retrieved data to JSON file. """
    file_name = f'{start_date}_{search_id}_{cursor - 100}.json'
    save_directory = 'scraper/data'
    file_path = os.path.join(save_directory, file_name)
    json_string = json.dumps(videos)
    with open(file_path, 'w') as f:
        json.dump(json_string, f)
    return


def save_video_to_db(video):
    tt_user, _ = TikTokUser.objects.get_or_create(name=video.get('username'))

    new_video, _ = TikTokVideo.objects.get_or_create(
        video_id=video.get('id'),
        video_description=video.get('video_description'),
        create_time=get_datetime_from_unix_ts(video.get('create_time')),
        username=tt_user,

        comment_count=video.get('comment_count'),
        like_count=video.get('like_count'),
        share_count=video.get('share_count'),
        view_count=video.get('view_count'),

        music_id=video.get('music_id'),
        region_code=video.get('region_code'),
    )

    video_hashtags = []
    for hashtag in video['hashtag_names']:
        video_hashtags.append(Hashtag.objects.get_or_create(name=hashtag)[0])
    new_video.hashtags.set(video_hashtags)
    return


def save_videos_to_db(videos):
    for video in videos:
        try:
            save_video_to_db(video)
        except Exception as e:
            logging.error(
                f'Video: {video.get("id")}; Exception: {e}'
            )
    return


def get_tt_videos():
    configure_logging()
    access_token = request_access_token()

    # Set query parameter.
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

    while has_more == True:
        response = scrape_videos_pagination(
            url, usernames, hashtags, max_count,
            start_date, end_date, headers, search_id, cursor
        )
        logging.info(f'Response status code: {response.status_code}')
        temp_data = response.json()

        if (temp_data['error']['code'] == 'internal_error') | (temp_data['error']['code'] == 'invalid_params'):
            error_counter += 1
            logging.warning(f'Error encountered: {temp_data["error"]["message"]} ({error_counter})')
            logging.warning(f'Error code: {temp_data["error"]["code"]}')

            # Killswitch after 20 consecutive errors.
            if error_counter >= 20:
                has_more = False
                logging.error(
                    f'Stopping after {error_counter} consecutive errors. '
                    f'Last error: {temp_data["error"]["message"]}'
                )
            else:
                time.sleep(10)
        else:
            error_counter = 0
            logging.info(
                f'Request successful. Cursor: {temp_data["data"]["cursor"]}, '
                f'Has More: {temp_data["data"]["has_more"]}'
            )

            # Update query parameter based on previous request.
            cursor = temp_data['data']['cursor']
            has_more = temp_data['data']['has_more']
            search_id = temp_data['data']['search_id']

            retrieved_data = temp_data['data']['videos']
            #save_videos_to_file(retrieved_data, start_date, search_id, cursor)
            save_videos_to_db(retrieved_data)

            time.sleep(10)

            if not has_more:
                logging.info(
                    f'Report for scraping {get_formatted_date()}. '
                    f'Successfully scraped {cursor} videos'
                )

    # Add this to test IP-related issues.
    log_server_ip()
