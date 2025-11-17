"""YouTube service for fetching metadata and transcripts."""

import logging
import re
from datetime import datetime, timezone
from typing import List, Optional

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from src.models import VideoMetadata, Transcript

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for interacting with YouTube API and transcripts."""

    def __init__(self, api_key: str):
        """Initialize YouTube service."""
        self.youtube = build("youtube", "v3", developerKey=api_key)

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        pattern = r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_video_metadata(self, video_id: str) -> VideoMetadata:
        """
        Fetch video metadata from YouTube API.

        Args:
            video_id: YouTube video ID

        Returns:
            VideoMetadata object

        Raises:
            Exception: If video not found or API error
        """
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics", id=video_id
            )
            response = request.execute()

            if not response["items"]:
                raise ValueError(f"Video not found: {video_id}")

            video = response["items"][0]
            snippet = video["snippet"]
            statistics = video["statistics"]

            # Parse duration (ISO 8601 format)
            duration_str = video["contentDetails"]["duration"]
            duration = self._parse_duration(duration_str)

            # Parse published date
            published_at = datetime.fromisoformat(
                snippet["publishedAt"].replace("Z", "+00:00")
            )

            return VideoMetadata(
                video_id=video_id,
                title=snippet["title"],
                description=snippet["description"],
                channel_name=snippet["channelTitle"],
                duration=duration,
                published_at=published_at,
                view_count=int(statistics["viewCount"]),
                like_count=int(statistics["likeCount"]),
            )

        except Exception as e:
            logger.error(f"Error fetching video metadata: {e}")
            raise

    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
        if not match:
            return 0

        hours = int(match.group(1) or "0")
        minutes = int(match.group(2) or "0")
        seconds = int(match.group(3) or "0")

        return hours * 3600 + minutes * 60 + seconds

    def get_transcript(
        self, video_id: str, preferred_languages: List[str]
    ) -> Transcript:
        """
        Fetch video transcript.

        Args:
            video_id: YouTube video ID
            preferred_languages: List of preferred language codes (e.g., ['ru', 'en'])

        Returns:
            Transcript object

        Raises:
            Exception: If transcript not available
        """
        try:
            api = YouTubeTranscriptApi()
            transcript_data = api.fetch(video_id, languages=preferred_languages)
            text = " ".join([entry.text for entry in transcript_data])

            return Transcript(
                video_id=video_id,
                language=transcript_data.language_code,
                text=text
            )

        except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound) as e:
            raise Exception(str(e))
        except Exception as e:
            logger.error(f"Error fetching transcript: {e}")
            raise
