from django.utils import timezone

from .TikTok_Content_Scraper.TT_Scraper import TT_Scraper
from scraper.models import TikTokVideo_B, Hashtag, TikTokUser_B
from django.utils.timezone import make_aware
from datetime import datetime
import os
import logging
import traceback
import sys


logging.getLogger("django.db.backends").setLevel(logging.WARNING)


def setup_logger(mode, existing_logger=None):
    """Setup logger for a specific scrape session or return existing logger."""

    # If an existing logger is provided, return it
    if existing_logger:
        return existing_logger

    # Create logs directory if it doesn't exist
    log_dir = os.path.join('scraper', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Create a unique logger name for this mode
    logger_name = f'scraper_B_logger_{mode}'
    logger = logging.getLogger(logger_name)

    # Prevent duplicate handlers
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # Create timestamp for the log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'scraper_B_{mode}_{timestamp}.log')

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers only once
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Prevent log propagation to the root logger
        logger.propagate = False

    return logger


def get_datetime_from_ts(ts):
    """Convert timestamp to timezone-aware datetime.
    
    Args:
        ts: Unix timestamp or None
        
    Returns:
        timezone-aware datetime or current time if ts is None
    """
    if ts is None:
        return make_aware(datetime.now())
    naive_datetime = datetime.fromtimestamp(ts)
    return make_aware(naive_datetime)

def load_video_ids_from_db():
    """Load video IDs in batches of 1000 that haven't been scraped yet."""
    BATCH_SIZE = 1000
    video_ids = (
        TikTokVideo_B.objects
        .filter(scrape_date__isnull=True)
        .order_by('-scrape_priority', '-pk')
        .values_list('video_id', flat=True)[:BATCH_SIZE]
    )
    return video_ids

def save_tt_user_to_db(author_id, author_metadata, logger):
    logger.info(f"Processing user: {author_id}")
    tt_user, created = TikTokUser_B.objects.get_or_create(
        author_id=author_id
    )
    if created:
        logger.info(f"Created new user: {author_id}")
    else:
        logger.info(f"Found existing user: {author_id}")

    # If user info has already been scraped, keep original values and do not overwrite.
    if tt_user.scrape_success:
        return tt_user

    # Update user fields
    tt_user.username = author_metadata.get('username')
    tt_user.nick_name = author_metadata.get("name")
    tt_user.signature = author_metadata.get("signature")
    tt_user.create_time = author_metadata.get("create_time")
    tt_user.verified = author_metadata.get("verified")
    tt_user.ftc = author_metadata.get("ftc")
    tt_user.relation = author_metadata.get("relation")
    tt_user.open_favorite = author_metadata.get("open_favorite")
    tt_user.comment_setting = author_metadata.get("comment_setting")
    tt_user.duet_setting = author_metadata.get("duet_setting")
    tt_user.stitch_setting = author_metadata.get("stitch_setting")
    tt_user.private_account = author_metadata.get("private_account")
    tt_user.secret = author_metadata.get("secret")
    tt_user.is_ad_virtual = author_metadata.get("is_ad_virtual")
    tt_user.download_setting = author_metadata.get("download_setting")
    tt_user.recommend_reason = author_metadata.get("recommend_reason")
    tt_user.suggest_account_bind = author_metadata.get("suggest_account_bind")
    tt_user.scrape_success = True
    tt_user.scrape_date = timezone.now()
    tt_user.save()
    return tt_user

def save_video_to_db(video_data, logger=None):
    """Saves video data to database."""
    if logger is None:
        logger = setup_logger('save_video')

    video_metadata = video_data.get("video_metadata")
    file_metadata = video_data.get("file_metadata")
    music_metadata = video_data.get("music_metadata")
    author_metadata = video_data.get("author_metadata")
    #hashtags_metadata = video_data.get("hashtags_metadata")
    
    try:
        # Get video ID from video_metadata
        video_id = video_metadata.get('id')
        if not video_id:
            msg = "No video ID found in video_metadata"
            logger.error(msg)
            logger.error(f"Video metadata: {video_metadata}")
            return msg
            
        logger.info(f"Processing video data for ID: {video_id}")
        
        # Validate required metadata sections
        required_sections = ['video_metadata', 'file_metadata', 'music_metadata', 'author_metadata', 'hashtags_metadata']
        missing_sections = [section for section in required_sections if section not in video_data]
        if missing_sections:
            msg = f"Missing required metadata sections for video {video_id}: {missing_sections}"
            logger.error(msg)
            logger.error(f"Available sections: {list(video_data.keys())}")
            return msg
        
        # Create or update user
        # Check if the user already exists
        author_id = author_metadata.get("id", None)
        if author_id is None:
            msg = f"No author_id found in video data for video {video_id}"
            logger.error(msg)
            logger.error(f"Video data keys: {list(video_data.keys())}")
            tt_user = None
        else:
            tt_user = save_tt_user_to_db(author_id, author_metadata, logger)

        # Get or create video
        logger.info(f"Processing video: {video_id}")
        video, created = TikTokVideo_B.objects.get_or_create(video_id=video_id)
        if created:
            logger.info(f"Created new video: {video_id}")
        else:
            logger.info(f"Found existing video: {video_id}")

        # If video info has already been scraped, keep original values and do not overwrite.
        if video.scrape_success:
            return None

        # Update video fields
        video.video_description = video_metadata.get("description")  # Changed from video_description to description
        video.create_time = video_metadata.get("time_created")  # Changed from create_time to time_created
        video.author_id = tt_user  # Set the author_id field to the TikTokUser_B instance
        video.comment_count = video_metadata.get("commentcount")  # Changed from comment_count to commentcount
        video.like_count = video_metadata.get("diggcount")  # Changed from like_count to diggcount
        video.share_count = video_metadata.get("sharecount")  # Changed from share_count to sharecount
        video.view_count = video_metadata.get("playcount")  # Changed from view_count to playcount

        video.music_id = music_metadata.get("id")  # Changed from music_id to id
        video.region_code = video_metadata.get("location_created")  # Changed from region_code to location_created

        video.schedule_time = video_metadata.get("schedule_time")
        video.is_ad = video_metadata.get("is_ad")
        video.suggested_words = video_metadata.get("suggested_words")
        video.diggcount = video_metadata.get("diggcount")
        video.collectcount = video_metadata.get("collectcount")
        video.repostcount = video_metadata.get("repostcount")
        video.poi_name = video_metadata.get("poi_name")
        video.poi_address = video_metadata.get("poi_address")
        video.poi_city = video_metadata.get("poi_city")
        video.warn_info = video_metadata.get("warn_info")
        video.original_item = video_metadata.get("original_item")
        video.offical_item = video_metadata.get("offical_item")
        video.secret = video_metadata.get("secret")
        video.for_friend = video_metadata.get("for_friend")
        video.digged = video_metadata.get("digged")
        video.item_comment_status = video_metadata.get("item_comment_status")
        video.take_down = video_metadata.get("take_down")
        video.effect_stickers = video_metadata.get("effect_stickers")
        video.private_item = video_metadata.get("private_item")
        video.duet_enabled = video_metadata.get("duet_enabled")
        video.stitch_enabled = video_metadata.get("stitch_enabled")
        video.stickers_on_item = video_metadata.get("stickers_on_item")
        video.share_enabled = video_metadata.get("share_enabled")
        video.comments = video_metadata.get("comments")
        video.duet_display = video_metadata.get("duet_display")
        video.index_enabled = video_metadata.get("index_enabled")
        video.diversification_labels = video_metadata.get("diversification_labels")
        video.diversification_id = video_metadata.get("diversification_id")
        video.channel_tags = video_metadata.get("channel_tags")
        video.keyword_tags = video_metadata.get("keyword_tags")
        video.is_ai_gc = video_metadata.get("is_ai_gc")
        video.ai_gc_description = video_metadata.get("ai_gc_description")

        video.filepath = file_metadata.get("filepath")
        video.duration = file_metadata.get("duration")
        video.height = file_metadata.get("height")
        video.width = file_metadata.get("width")
        video.ratio = file_metadata.get("ratio")
        video.volume_loudness = file_metadata.get("volume_loudness")
        video.volume_peak = file_metadata.get("volume_peak")
        video.has_original_audio = file_metadata.get("has_original_audio")
        video.enable_audio_caption = file_metadata.get("enable_audio_caption")
        video.no_caption_reason = file_metadata.get("no_caption_reason")

        video.scrape_date = timezone.now()

        # Handle mentions (ManyToManyField)
        mentions = video_metadata.get("mentions")
        if mentions:
            # Create or get TikTokUser_B objects for each mentioned user
            mentioned_users = []
            for author_id in mentions:
                mentioned_user, created = TikTokUser_B.objects.get_or_create(
                    author_id=author_id
                )
                if created:
                    mentioned_user.username = f"temp_user_{author_id}",  # Temporary username until we get the actual username
                    mentioned_user.save()

                mentioned_users.append(mentioned_user)
            
            if mentioned_users:
                video.mentions.set(mentioned_users)
            else:
                video.mentions.clear()
        else:
            video.mentions.clear()

        # Handle hashtags (ManyToManyField)
        hashtags = video_metadata.get('hashtags', [])  # Get hashtag names from video_metadata
        if hashtags:
            # Create or get hashtag objects by name
            hashtag_objects = []
            for hashtag_name in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
                hashtag_objects.append(hashtag)
            
            if hashtag_objects:
                video.hashtags.set(hashtag_objects)
            else:
                video.hashtags.clear()
        else:
            video.hashtags.clear()

        video.scrape_success = True
        video.save()
        logger.info(f"Successfully saved video meta data to db: {video_id}")
        return None

    except Exception as e:
        logger.error(f"Error saving video {video_data.get('id', 'unknown')}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Video data: {video_data}")
        raise


# create a new class, that inherits the TT_Scraper
class TT_Scraper_DB_metadata(TT_Scraper):
    def __init__(self, wait_time=0.35, output_files_fp="data/", logger=None):
        super().__init__(wait_time, output_files_fp)
        self.log = logger if logger else setup_logger('scraper')

    def scrape(self, id=None, scrape_content=False, download_metadata=False, download_content=False):
        """Override scrape method to handle metadata retrieval and database storage."""
        try:
            metadata_package, success = super().scrape(id=id, scrape_content=scrape_content, download_metadata=False, download_content=scrape_content)
            if metadata_package:
                msg = save_video_to_db(metadata_package, logger=self.log)

                if msg is not None:
                    # Add scraping exception to db.
                    video = TikTokVideo_B.objects.filter(video_id=id).first()
                    if video is not None:
                        video.scrape_success = False
                        video.scrape_status = msg
                        video.scrape_date = timezone.now()
                        video.save()
                    else:
                        self.log.error(f'A: video is none: {id}')
                    return False
                else:
                    self.log.info(f"Successfully processed video {id}")
                    return True
            else:
                msg = f"Failed to get metadata for video {id}"
                self.log.error(msg)
                video = TikTokVideo_B.objects.filter(video_id=id).first()
                if video is not None:
                    video.scrape_success = False
                    video.scrape_status = msg
                    video.scrape_date = timezone.now()
                    video.save()
                else:
                    self.log.error(f'B: video is none: {id}')
                return False
        except Exception as e:
            self.log.error(f"Error in scrape method for video {id}: {str(e)}")
            self.log.error(f"Traceback: {traceback.format_exc()}")
            video = TikTokVideo_B.objects.filter(video_id=id).first()
            video.scrape_date = timezone.now()
            video.save()
            return False

    def scrape_list(self, ids, scrape_content=False, batch_size=None, clear_console=True, total_videos=0, already_scraped_count=0, total_errors=0):
        """Override scrape_list to handle multiple videos."""
        self.log.info(f"Starting to scrape {len(ids)} videos")
        
        for video_id in ids:
            try:
                # Check if video has already been processed
                if TikTokVideo_B.objects.filter(video_id=video_id, scrape_date__isnull=False).exists():
                    self.log.info(f"Video {video_id} has already been processed, skipping")
                    continue
                    
                # Scrape and save in one step
                success = self.scrape(id=video_id, scrape_content=scrape_content)
                if not success:
                    self.log.error(f"Failed to process video {video_id}")
            except Exception as e:
                self.log.error(f"Error processing video {video_id}: {str(e)}")
                self.log.error(f"Traceback: {traceback.format_exc()}")

    def insert_metadata_to_db(self, metadata_package):
        """Save video metadata to database."""
        # TODO: Delete?
        msg = save_video_to_db(metadata_package, logger=self.log)
        return msg


def collect_metadata_for_all(scraper=None, logger=None, test_mode=False, scrape_content=False):
    """Collect metadata for all videos in the database."""
    if logger is None:
        logger = setup_logger('collect_metadata')
    
    # Create TT_Scraper_DB_metadata instance with the same logger
    if scraper is None:
        scraper = TT_Scraper_DB_metadata(wait_time=0.35, logger=logger)

    while True:

        try:
            video_ids = load_video_ids_from_db()
            if len(video_ids) == 0:
                break

            logger.info(f'Loaded {len(video_ids)} videos from database')

            if test_mode:
                video_ids = video_ids[:10]
                logger.info(f'Test mode: Processing first {len(video_ids)} videos')

            # Redirect stdout to prevent binary data from being printed
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

            try:
                scraper.scrape_list(video_ids, scrape_content=scrape_content)
            finally:
                if test_mode:
                    break

                sys.stdout.close()
                sys.stdout = original_stdout

            logger.info('Scraping completed successfully')

        except Exception as e:
            logger.error(f"Error in collect_metadata_for_all: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
