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
import warnings

warnings.filterwarnings('ignore', category=Warning)

load_dotenv()

def setup_logger(mode, existing_logger=None):
    """Setup logger for a specific scrape session or return existing logger."""
    if existing_logger:
        return existing_logger
        
    # Create logs directory if it doesn't exist
    log_dir = os.path.join('scraper', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Create timestamp for the log file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'scraper_{mode}_{timestamp}.log')

    # Create a new logger
    logger = logging.getLogger(f'scraper_logger_{timestamp}')
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Add only file handler
    logger.addHandler(file_handler)

    return logger

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


def log_server_ip(logger=None):
    """Added to test IP-related issues."""
    if logger is None:
        logger = setup_logger('ip_check')
        
    try:
        response = requests.get('https://api.ipify.org?format=json')
        logger.info(f'Server IP: {response.json()["ip"]}')
    except Exception as e:
        logger.error(f"Error checking server IP: {str(e)}")
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


def make_api_request(url, headers, query_params, max_retries=3, retry_delay=10, logger=None):
    """Generic function to make API requests with retry logic."""
    if logger is None:
        logger = setup_logger('api_request')
        
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(query_params))
            #print(response)
            #print(response.status_code)
            logger.debug(f"Response status code: {response.status_code}")
            return response.json()
        except (json.JSONDecodeError, requests.RequestException) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1}/{max_retries}: Request failed: {str(e)}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                continue
            logger.error(f"Failed after {max_retries} attempts: {str(e)}")
            raise


def build_query_params(usernames, hashtags=None, start_date=None, end_date=None, 
                      cursor=0, search_id=None, max_count=100, logger=None):
    """Build query parameters for TikTok API."""
    if logger is None:
        logger = setup_logger('query_builder')
    
    query = {
        'or': [
            {
                'operation': 'IN',
                'field_name': 'username',
                'field_values': usernames
            }
        ],
        'and': [
            {
                'operation': 'IN',
                'field_name': 'region_code',
                'field_values': ['DE', 'de', 'RU', 'ru', 'AT', 'at', 'ch', 'CH']
            }
        ]
    }
    
    if hashtags:
        query['or'].append({
            'operation': 'IN',
            'field_name': 'hashtag_name',
            'field_values': hashtags
        })

    params = {
        'query': query,
        'max_count': max_count,
        'is_random': False,
        'start_date': start_date,
        'end_date': end_date,
        'cursor': cursor
    }
    
    if search_id:
        params['search_id'] = search_id
        
    return params


def process_api_response(response_data, error_counter=0, logger=None):
    """Process API response and handle errors."""
    if logger is None:
        logger = setup_logger('response_processor')
    
    if 'error' in response_data and response_data['error'].get('code') in ['internal_error', 'invalid_params']:
        error_counter += 1
        logger.warning(f'Error encountered: {response_data["error"]["message"]} ({error_counter})')
        logger.warning(f'Error code: {response_data["error"]["code"]}')
        return None, error_counter, True
        
    if 'data' not in response_data:
        logger.error(f"Unexpected API response format: {response_data}")
        return None, error_counter, False
    
    # Log cursor information
    cursor_info = {
        "cursor": response_data["data"].get("cursor", None),
        "has_more": response_data["data"].get("has_more", False),
        "search_id": response_data["data"].get("search_id", "")
    }
    logger.info(f"Query cursor info: {json.dumps(cursor_info)}")
        
    return response_data['data'], 0, True  # Reset error counter on success


def get_tt_videos_new_day(specific_date=None, logger=None, test_mode=False):
    """Scrape videos for a specific day or the default past day."""
    logger = setup_logger('new_day', logger)
    logger.info('========Scraping I new day videos========')
    if test_mode:
        logger.info('TEST MODE: Will stop after 5 successful requests')
    
    access_token = request_access_token()
    
    start_date = end_date = specific_date or get_formatted_date()
    scrape_date = timezone.now().timestamp()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    cursor = 0
    search_id = ''
    has_more = True
    error_counter = 0
    
    request_count = 0
    while has_more and error_counter < 20:
        try:
            query_params = build_query_params(
                usernames=get_username_list(),
                hashtags=HASHTAG_LIST,
                start_date=start_date,
                end_date=end_date,
                cursor=cursor,
                search_id=search_id,
                logger=logger
            )
            
            response_data = make_api_request(get_video_query_url(), headers, query_params, logger=logger)
            data, error_counter, should_continue = process_api_response(response_data, error_counter, logger=logger)
            
            if not should_continue:
                break
                
            if data:
                if 'videos' in data:
                    save_videos_to_db(data['videos'], scrape_date, logger)
                    request_count += 1
                    if test_mode and request_count >= 5:
                        logger.info('TEST MODE: Completed 5 successful requests')
                        return
                
                cursor = data.get('cursor', 0)
                has_more = data.get('has_more', False)
                search_id = data.get('search_id', '')
                
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}", exc_info=True)
            raise


def get_tt_videos_update_account_data(logger=None, test_mode=False):
    """Update historical account data."""
    logger = setup_logger('account_update', logger)
    logger.info('========Scraping II update account data========')
    if test_mode:
        logger.info('TEST MODE: Will stop after 5 successful requests')
    
    access_token = request_access_token()
    
    start_date = "20250101"
    end_date = get_formatted_date(delay=5)
    
    logger.info(f"Generating date range from {start_date} to {end_date}")
    date_ranges = generate_date_range(start_date, end_date)
    logger.info(f"Generated {len(date_ranges)} date ranges")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    scrape_date = timezone.now().timestamp()
    usernames = get_username_list()
    
    request_count = 0
    for date_range in date_ranges:
        cursor = 0
        search_id = ''
        has_more = True
        error_counter = 0
        
        while has_more and error_counter < 20:
            try:
                query_params = build_query_params(
                    usernames=usernames,
                    start_date=date_range[0],
                    end_date=date_range[1],
                    cursor=cursor,
                    search_id=search_id,
                    logger=logger
                )
                
                response_data = make_api_request(get_video_query_url(), headers, query_params, logger=logger)
                data, error_counter, should_continue = process_api_response(response_data, error_counter, logger=logger)
                
                if not should_continue:
                    break
                    
                if data:
                    if 'videos' in data:
                        save_videos_to_db(data['videos'], scrape_date, logger)
                        request_count += 1
                        if test_mode and request_count >= 5:
                            logger.info('TEST MODE: Completed 5 successful requests')
                            return
                    
                    cursor = data.get('cursor', 0)
                    has_more = data.get('has_more', False)
                    search_id = data.get('search_id', '')
                    
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}", exc_info=True)
                raise
    
    log_server_ip(logger=logger)


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


def save_video_to_db(video_data, scrape_ts=None, logger=None):
    """Saves video data to database."""
    if logger is None:
        logger = setup_logger('save_video')
        
    try:
        tt_user, _ = TikTokUser.objects.get_or_create(name=video_data.get('username'))

        video = TikTokVideo.objects.filter(video_id=video_data.get('id')).first()
        if video is None:
            video = TikTokVideo.objects.create(
                video_id=video_data.get('id'),
                video_description=video_data.get('video_description'),
                create_time=get_datetime_from_unix_ts(video_data.get('create_time')),
                author_id=tt_user,
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
        logger.error(f"Error saving video {video_data.get('id', 'unknown')}: {str(e)}")
        logger.error(f"Video data: {video_data}")
        raise


def save_videos_to_db(videos, scrape_ts=None, logger=None):
    """Save multiple videos to database."""
    if logger is None:
        logger = setup_logger('save_videos')
    
    logger.info(f"Starting to save batch of {len(videos)} videos")
    success_count = 0
    
    for video in videos:
        try:
            save_video_to_db(video, scrape_ts, logger)
            success_count += 1
        except Exception as e:
            logger.error(f'Video: {video.get("id")}; Exception: {e}')
    
    logger.info(f"Successfully saved {success_count}/{len(videos)} videos from batch")
