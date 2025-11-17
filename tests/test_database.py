"""Tests for database module."""

import pytest
from datetime import datetime, timezone
from src.database import Database
from src.models import VideoMetadata, Transcript, VideoSummary, ConversationMessage


@pytest.fixture
def db():
    """Create an in-memory database for testing."""
    return Database("sqlite:///:memory:")


class TestVideoMetadata:
    """Tests for video metadata operations."""

    def test_save_and_get_metadata(self, db):
        """Test saving and retrieving video metadata."""
        metadata = VideoMetadata(
            video_id="test123",
            title="Test Video",
            description="Test description",
            channel_name="Test Channel",
            duration=600,
            published_at=datetime(2024, 1, 1),
            view_count=1000,
            like_count=100,
        )

        db.save_video_metadata(metadata)
        retrieved = db.get_video_metadata("test123")

        assert retrieved is not None
        assert retrieved.video_id == "test123"
        assert retrieved.title == "Test Video"
        assert retrieved.channel_name == "Test Channel"

    def test_get_nonexistent_metadata(self, db):
        """Test retrieving non-existent metadata."""
        result = db.get_video_metadata("nonexistent")
        assert result is None

    def test_update_metadata(self, db):
        """Test updating existing metadata."""
        metadata1 = VideoMetadata(
            video_id="test123",
            title="Original Title",
            description="Original description",
            channel_name="Channel",
            duration=600,
            published_at=datetime(2024, 1, 1),
            view_count=1000,
            like_count=100,
        )

        db.save_video_metadata(metadata1)

        metadata2 = VideoMetadata(
            video_id="test123",
            title="Updated Title",
            description="Updated description",
            channel_name="Channel",
            duration=600,
            published_at=datetime(2024, 1, 1),
            view_count=2000,
            like_count=200,
        )

        db.save_video_metadata(metadata2)
        retrieved = db.get_video_metadata("test123")

        assert retrieved.title == "Updated Title"
        assert retrieved.view_count == 2000


class TestTranscript:
    """Tests for transcript operations."""

    def test_save_and_get_transcript(self, db):
        """Test saving and retrieving transcript."""
        transcript = Transcript(
            video_id="test123", language="en", text="This is a test transcript."
        )

        db.save_transcript(transcript)
        retrieved = db.get_transcript("test123", "en")

        assert retrieved is not None
        assert retrieved.video_id == "test123"
        assert retrieved.language == "en"
        assert retrieved.text == "This is a test transcript."

    def test_get_transcript_different_language(self, db):
        """Test retrieving transcript in different language."""
        transcript = Transcript(
            video_id="test123", language="en", text="English transcript"
        )

        db.save_transcript(transcript)
        retrieved = db.get_transcript("test123", "ru")

        assert retrieved is None

    def test_duplicate_transcript_not_saved(self, db):
        """Test that duplicate transcripts are not saved."""
        transcript1 = Transcript(
            video_id="test123", language="en", text="First version"
        )
        transcript2 = Transcript(
            video_id="test123", language="en", text="Second version"
        )

        db.save_transcript(transcript1)
        db.save_transcript(transcript2)

        retrieved = db.get_transcript("test123", "en")
        # Should still be the first version
        assert retrieved.text == "First version"


class TestVideoSummary:
    """Tests for video summary operations."""

    def test_save_and_get_summary(self, db):
        """Test saving and retrieving summary."""
        summary = VideoSummary(
            video_id="test123",
            summary="This is a test summary.",
            created_at=datetime.now(timezone.utc),
        )

        db.save_summary(summary)
        retrieved = db.get_summary("test123")

        assert retrieved is not None
        assert retrieved.video_id == "test123"
        assert retrieved.summary == "This is a test summary."

    def test_get_nonexistent_summary(self, db):
        """Test retrieving non-existent summary."""
        result = db.get_summary("nonexistent")
        assert result is None


class TestConversationMessages:
    """Tests for conversation message operations."""

    def test_save_and_get_messages(self, db):
        """Test saving and retrieving conversation messages."""
        msg1 = ConversationMessage(
            user_id=123,
            video_id="test123",
            role="user",
            content="What is this video about?",
            created_at=datetime.now(timezone.utc),
        )

        msg2 = ConversationMessage(
            user_id=123,
            video_id="test123",
            role="assistant",
            content="This video is about...",
            created_at=datetime.now(timezone.utc),
        )

        db.save_message(msg1)
        db.save_message(msg2)

        history = db.get_conversation_history(123, "test123")

        assert len(history) == 2
        assert history[0].role == "user"
        assert history[1].role == "assistant"

    def test_conversation_history_limit(self, db):
        """Test conversation history respects limit."""
        for i in range(60):
            msg = ConversationMessage(
                user_id=123,
                video_id="test123",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                created_at=datetime.now(timezone.utc),
            )
            db.save_message(msg)

        history = db.get_conversation_history(123, "test123", limit=10)
        assert len(history) == 10

    def test_get_last_video_for_user(self, db):
        """Test getting last video for user."""
        msg1 = ConversationMessage(
            user_id=123,
            video_id="video1",
            role="user",
            content="First video",
            created_at=datetime(2024, 1, 1),
        )

        msg2 = ConversationMessage(
            user_id=123,
            video_id="video2",
            role="user",
            content="Second video",
            created_at=datetime(2024, 1, 2),
        )

        db.save_message(msg1)
        db.save_message(msg2)

        last_video = db.get_last_video_for_user(123)
        assert last_video == "video2"

    def test_get_last_video_no_messages(self, db):
        """Test getting last video when user has no messages."""
        result = db.get_last_video_for_user(999)
        assert result is None
