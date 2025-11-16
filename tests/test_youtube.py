"""Tests for YouTube service."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.youtube import YouTubeService
from src.models import VideoMetadata, Transcript


@pytest.fixture
def youtube_service():
    """Create a YouTube service instance for testing."""
    return YouTubeService(api_key="test_api_key")


class TestExtractVideoId:
    """Tests for video ID extraction."""

    def test_extract_from_watch_url(self, youtube_service):
        """Test extraction from standard watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert youtube_service.extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_short_url(self, youtube_service):
        """Test extraction from short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert youtube_service.extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_mobile_url(self, youtube_service):
        """Test extraction from mobile URL."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert youtube_service.extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_embed_url(self, youtube_service):
        """Test extraction from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert youtube_service.extract_video_id(url) == "dQw4w9WgXcQ"

    def test_extract_from_direct_id(self, youtube_service):
        """Test extraction from direct video ID."""
        video_id = "dQw4w9WgXcQ"
        assert youtube_service.extract_video_id(video_id) == "dQw4w9WgXcQ"

    def test_extract_invalid_url(self, youtube_service):
        """Test extraction from invalid URL."""
        url = "https://example.com/video"
        assert youtube_service.extract_video_id(url) is None


class TestParseDuration:
    """Tests for duration parsing."""

    def test_parse_hours_minutes_seconds(self, youtube_service):
        """Test parsing full duration."""
        duration = "PT1H30M45S"
        assert youtube_service._parse_duration(duration) == 5445

    def test_parse_minutes_seconds(self, youtube_service):
        """Test parsing minutes and seconds."""
        duration = "PT5M30S"
        assert youtube_service._parse_duration(duration) == 330

    def test_parse_only_seconds(self, youtube_service):
        """Test parsing only seconds."""
        duration = "PT45S"
        assert youtube_service._parse_duration(duration) == 45

    def test_parse_only_hours(self, youtube_service):
        """Test parsing only hours."""
        duration = "PT2H"
        assert youtube_service._parse_duration(duration) == 7200


class TestGetVideoMetadata:
    """Tests for video metadata fetching."""

    @patch("src.youtube.build")
    def test_get_video_metadata_success(self, mock_build, youtube_service):
        """Test successful metadata fetching."""
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        mock_response = {
            "items": [
                {
                    "id": "test_video_id",
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test description",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2024-01-01T00:00:00Z",
                    },
                    "contentDetails": {"duration": "PT10M30S"},
                    "statistics": {
                        "viewCount": "1000",
                        "likeCount": "100",
                    },
                }
            ]
        }

        mock_youtube.videos().list().execute.return_value = mock_response
        youtube_service.youtube = mock_youtube

        metadata = youtube_service.get_video_metadata("test_video_id")

        assert metadata.video_id == "test_video_id"
        assert metadata.title == "Test Video"
        assert metadata.description == "Test description"
        assert metadata.channel_name == "Test Channel"
        assert metadata.duration == 630
        assert metadata.view_count == 1000
        assert metadata.like_count == 100

    @patch("src.youtube.build")
    def test_get_video_metadata_not_found(self, mock_build, youtube_service):
        """Test metadata fetching for non-existent video."""
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        mock_youtube.videos().list().execute.return_value = {"items": []}
        youtube_service.youtube = mock_youtube

        with pytest.raises(ValueError, match="Video not found"):
            youtube_service.get_video_metadata("invalid_id")


class TestGetTranscript:
    """Tests for transcript fetching."""

    @patch("src.youtube.YouTubeTranscriptApi")
    def test_get_transcript_preferred_language(self, mock_api, youtube_service):
        """Test getting transcript in preferred language."""
        # Create mock instance
        mock_instance = Mock()
        mock_api.return_value = mock_instance

        # Mock transcript data - create Mock objects with .text attribute (like FetchedTranscriptSnippet)
        mock_transcript_data = Mock()

        # Create mock snippet objects with text attribute
        snippet1 = Mock()
        snippet1.text = "Hello"
        snippet2 = Mock()
        snippet2.text = "World"

        transcript_entries = [snippet1, snippet2]
        mock_transcript_data.__iter__ = Mock(return_value=iter(transcript_entries))
        mock_transcript_data.language_code = "ru"

        mock_instance.fetch.return_value = mock_transcript_data

        transcript = youtube_service.get_transcript("test_id", ["ru", "en"])

        assert transcript.video_id == "test_id"
        assert transcript.language == "ru"
        assert transcript.text == "Hello World"
        mock_instance.fetch.assert_called_once_with("test_id", languages=["ru", "en"])

    @patch("src.youtube.YouTubeTranscriptApi")
    def test_get_transcript_fallback_english(self, mock_api, youtube_service):
        """Test falling back to English transcript."""
        # Create mock instance
        mock_instance = Mock()
        mock_api.return_value = mock_instance

        # Mock English transcript data with snippet object
        mock_transcript_data = Mock()

        snippet = Mock()
        snippet.text = "Hello"

        transcript_entries = [snippet]
        mock_transcript_data.__iter__ = Mock(return_value=iter(transcript_entries))
        mock_transcript_data.language_code = "en"

        mock_instance.fetch.return_value = mock_transcript_data

        transcript = youtube_service.get_transcript("test_id", ["ru", "en"])

        assert transcript.language == "en"
        assert transcript.text == "Hello"
        mock_instance.fetch.assert_called_once_with("test_id", languages=["ru", "en"])
